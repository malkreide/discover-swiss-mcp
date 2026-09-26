"""Outbound request hardening — SSRF, DNS rebinding and egress control.

Three code-layer defences, following ``openlex-mcp/net.py`` rather than
inventing a second pattern:

* **HTTPS only.** The Infocenter is HTTPS-only; there is no legacy-host
  exception here, so the check has no escape hatch to maintain.
* **Egress allow-list.** Only ``api.discover.swiss`` may be reached, and the
  list is a ``frozenset`` — not mutable at runtime.
* **SSRF IP block plus DNS pinning.** The host is resolved **once**, every
  resulting address is checked against the private/loopback/link-local/metadata
  ranges, and the connection is pinned to the checked IP while the ``Host``
  header and the TLS SNI keep the original name. That closes the TOCTOU window
  a second lookup at connect time would open.

Redirects are followed manually so that **every** hop runs the full chain
again. A redirect on a POST is refused outright instead: replaying a request
body at a new target is a decision, not a detail, and the Infocenter does not
redirect its ``/search`` endpoint.

**Two kinds of failure, two types** (audit SEC-028). A request the policy
forbids raises :class:`EgressError` and is never retried: asking again cannot
make a forbidden host allowed. A name that does not resolve raises
:class:`ResolutionError`, a :class:`httpx.ConnectError`, so the client's retry
ladder treats it like any other connection failure. Sharing one type made an
empty DNS answer read as "blocked by egress policy" and let a raw
``socket.gaierror`` escape untyped.
"""

from __future__ import annotations

import asyncio
import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx

# The one host this server talks to. PROD and TEST differ in the path
# (`/info/v2` vs `/test/info/v2`), not in the host, so one entry covers both.
EGRESS_ALLOWLIST: frozenset[str] = frozenset({"api.discover.swiss"})

# Non-routable and internal ranges, including the cloud metadata endpoint
# 169.254.169.254 — the address that turns a naive fetcher into a credential
# leak on every major cloud.
BLOCKED_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = tuple(
    ipaddress.ip_network(n)
    for n in (
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    )
)

MAX_REDIRECTS = 5


class EgressError(ValueError):
    """An outbound request was stopped by the egress policy. Never retried."""


class ResolutionError(httpx.ConnectError):
    """The target name did not resolve. Transient, retried like a connect error."""


def _is_blocked_ip(ip_str: str) -> bool:
    """Whether an address lies in a range this server must never contact.

    IPv6 forms that carry an IPv4 address are unwrapped first — mapped
    (``::ffff:169.254.169.254``), 6to4 (``2002::/16``) and Teredo. Unwrapped,
    ``ipaddress`` compares across versions as not-contained, so the mapped form
    of the metadata endpoint passed the list unchanged (audit SEC-004).

    The address properties are checked besides the list, so a range the list
    does not spell out (multicast, reserved, unspecified) is caught too.
    ``is_private`` is deliberately not among them: it also covers the
    documentation ranges (TEST-NET), which the unit tests pin to and which
    carry no internal service.
    """
    ip = ipaddress.ip_address(ip_str)
    if isinstance(ip, ipaddress.IPv6Address):
        embedded = ip.ipv4_mapped or ip.sixtofour or (ip.teredo[1] if ip.teredo else None)
        if embedded is not None:
            ip = embedded
    if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
        return True
    if ip.is_unspecified:
        return True
    return any(ip in net for net in BLOCKED_NETWORKS)


def assert_host_allowed(host: str, allowlist: frozenset[str] = EGRESS_ALLOWLIST) -> None:
    """Raise :class:`EgressError` if the host is not on the allow-list.

    ``allowlist`` defaults to the Infocenter. The only other caller is the
    OAuth token introspection (:mod:`discover_swiss_mcp.auth`), which passes a
    frozenset of exactly the one introspection host, fixed at start-up.
    """
    if host not in allowlist:
        raise EgressError(f"Host {host!r} is not on the egress allow-list ({sorted(allowlist)}).")


async def _resolve(host: str, port: int) -> list[str]:
    """Resolve a host **once**, preserving the order the resolver returned."""
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError) as exc:
        raise ResolutionError(f"DNS lookup for {host!r} failed ({type(exc).__name__}).") from exc
    ips: list[str] = []
    for info in infos:
        ip = info[4][0]
        if ip not in ips:
            ips.append(ip)
    return ips


async def assert_url_allowed(url: str, allowlist: frozenset[str] = EGRESS_ALLOWLIST) -> list[str]:
    """Check scheme, host allow-list and every resolved IP. Returns the IPs."""
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        raise EgressError(f"URL without a host: {url!r}.")
    if parsed.scheme != "https":
        raise EgressError(f"Scheme {parsed.scheme!r} is not allowed; HTTPS is required.")
    assert_host_allowed(host, allowlist)
    ips = await _resolve(host, parsed.port or 443)
    if not ips:
        raise ResolutionError(f"No DNS answer for {host!r}.")
    for ip in ips:
        if _is_blocked_ip(ip):
            raise EgressError(
                f"Blocked address {ip} for {host!r} (private/loopback/link-local/metadata range)."
            )
    return ips


def _pin_url(url: str, ip: str) -> str:
    """Replace the URL's host with the resolved IP (DNS pinning)."""
    parsed = urlparse(url)
    host = f"[{ip}]" if ":" in ip else ip
    netloc = f"{host}:{parsed.port}" if parsed.port else host
    return urlunparse(parsed._replace(netloc=netloc))


async def safe_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: Any | None = None,
    form_body: dict[str, str] | None = None,
    auth: tuple[str, str] | None = None,
    allowlist: frozenset[str] = EGRESS_ALLOWLIST,
    max_redirects: int = MAX_REDIRECTS,
) -> tuple[httpx.Response, str]:
    """HTTPS + allow-list + IP block + DNS pinning + redirect gate.

    Returns:
        ``(response, final_url)`` where ``final_url`` is the logical,
        host-based URL the answer was read from.
    """
    method = method.upper()
    current = url
    for _ in range(max_redirects + 1):
        ips = await assert_url_allowed(current, allowlist)
        host = urlparse(current).hostname or ""
        pinned = _pin_url(current, ips[0])
        request_headers = {**(headers or {}), "Host": host}
        response = await client.request(
            method,
            pinned,
            headers=request_headers,
            params=params,
            json=json_body,
            data=form_body,
            auth=auth,
            extensions={"sni_hostname": host},
        )
        if response.is_redirect and response.headers.get("location"):
            if method != "GET":
                raise EgressError(
                    f"{method} {url} answered with a redirect; a request body is not replayed at a new target."
                )
            current = str(httpx.URL(current).join(response.headers["location"]))
            # Query parameters already travelled with the first hop and are
            # part of the Location the source sent back.
            params = None
            continue
        return response, current
    raise EgressError(f"Too many redirects (> {max_redirects}).")
