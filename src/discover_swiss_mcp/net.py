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
    """An outbound request was stopped by one of the defences above."""


def _is_blocked_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return any(ip in net for net in BLOCKED_NETWORKS)


def assert_host_allowed(host: str) -> None:
    """Raise :class:`EgressError` if the host is not on the allow-list."""
    if host not in EGRESS_ALLOWLIST:
        raise EgressError(
            f"Host {host!r} is not on the egress allow-list ({sorted(EGRESS_ALLOWLIST)})."
        )


async def _resolve(host: str, port: int) -> list[str]:
    """Resolve a host **once**, preserving the order the resolver returned."""
    loop = asyncio.get_running_loop()
    infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    ips: list[str] = []
    for info in infos:
        ip = info[4][0]
        if ip not in ips:
            ips.append(ip)
    return ips


async def assert_url_allowed(url: str) -> list[str]:
    """Check scheme, host allow-list and every resolved IP. Returns the IPs."""
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        raise EgressError(f"URL without a host: {url!r}.")
    if parsed.scheme != "https":
        raise EgressError(f"Scheme {parsed.scheme!r} is not allowed; HTTPS is required.")
    assert_host_allowed(host)
    ips = await _resolve(host, parsed.port or 443)
    if not ips:
        raise EgressError(f"No DNS answer for {host!r}.")
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
        ips = await assert_url_allowed(current)
        host = urlparse(current).hostname or ""
        pinned = _pin_url(current, ips[0])
        request_headers = {**(headers or {}), "Host": host}
        response = await client.request(
            method,
            pinned,
            headers=request_headers,
            params=params,
            json=json_body,
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
