"""Outbound hardening: allow-list, IP block, DNS pinning, redirect gate."""

from __future__ import annotations

import asyncio
import socket

import httpx
import pytest
import respx

from discover_swiss_mcp import net

# Captured at import, before the autouse fixture in conftest.py replaces
# `net._resolve` for every test — the only way to exercise the real resolver.
_REAL_RESOLVE = net._resolve


async def test_only_the_infocenter_host_is_reachable() -> None:
    with pytest.raises(net.EgressError):
        await net.assert_url_allowed("https://example.org/info/v2/search")


async def test_http_is_refused_even_for_the_allowed_host() -> None:
    with pytest.raises(net.EgressError):
        await net.assert_url_allowed("http://api.discover.swiss/info/v2/status")


@pytest.mark.parametrize(
    "ip",
    ["127.0.0.1", "10.0.0.5", "192.168.1.1", "169.254.169.254", "::1"],
)
async def test_private_and_metadata_addresses_are_blocked(monkeypatch, ip: str) -> None:
    """169.254.169.254 is the cloud metadata endpoint — the SSRF prize."""

    async def _resolve(_host: str, _port: int) -> list[str]:
        return [ip]

    monkeypatch.setattr(net, "_resolve", _resolve)
    with pytest.raises(net.EgressError) as excinfo:
        await net.assert_url_allowed("https://api.discover.swiss/info/v2/status")
    assert ip in str(excinfo.value)


async def test_a_host_that_resolves_to_nothing_is_a_resolution_error(monkeypatch) -> None:
    """An empty DNS answer is transient, not a policy decision (audit SEC-028)."""

    async def _resolve(_host: str, _port: int) -> list[str]:
        return []

    monkeypatch.setattr(net, "_resolve", _resolve)
    with pytest.raises(net.ResolutionError) as excinfo:
        await net.assert_url_allowed("https://api.discover.swiss/info/v2/status")
    assert not isinstance(excinfo.value, net.EgressError)
    # The client's retry ladder catches `httpx.RequestError`; this is what
    # makes a resolution failure retried rather than fatal.
    assert isinstance(excinfo.value, httpx.RequestError)


async def test_a_resolver_error_is_typed_not_raw(monkeypatch) -> None:
    """`socket.gaierror` used to escape untyped; now it is a ResolutionError."""

    async def _fail(*_args, **_kwargs):
        raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")

    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", _fail)
    with pytest.raises(net.ResolutionError) as excinfo:
        await _REAL_RESOLVE("api.discover.swiss", 443)
    assert isinstance(excinfo.value.__cause__, socket.gaierror)


@pytest.mark.parametrize(
    "ip",
    [
        "::ffff:169.254.169.254",  # IPv4-mapped metadata endpoint (audit SEC-004)
        "::ffff:127.0.0.1",
        "::ffff:10.1.2.3",
        "2002:a9fe:a9fe::1",  # 6to4 wrapping 169.254.169.254
        "::",
        "0.0.0.0",
        "224.0.0.1",
        "240.0.0.1",
    ],
)
async def test_embedded_and_special_addresses_are_blocked(monkeypatch, ip: str) -> None:
    async def _resolve(_host: str, _port: int) -> list[str]:
        return [ip]

    monkeypatch.setattr(net, "_resolve", _resolve)
    with pytest.raises(net.EgressError):
        await net.assert_url_allowed("https://api.discover.swiss/info/v2/status")


@pytest.mark.parametrize("ip", ["203.0.113.10", "8.8.8.8", "::ffff:8.8.8.8", "2a00:1450::1"])
def test_public_and_documentation_addresses_pass(ip: str) -> None:
    """The counter-check: the extra rules do not block ordinary addresses."""
    assert net._is_blocked_ip(ip) is False


def test_pin_url_keeps_the_path_and_brackets_ipv6() -> None:
    assert (
        net._pin_url("https://api.discover.swiss/info/v2/status", "203.0.113.10")
        == "https://203.0.113.10/info/v2/status"
    )
    assert net._pin_url("https://api.discover.swiss/x", "2001:db8::1") == "https://[2001:db8::1]/x"


@respx.mock
async def test_the_request_goes_to_the_ip_and_keeps_the_host_name(monkeypatch) -> None:
    """DNS is resolved once; the connection is pinned so no second lookup can differ."""

    async def _resolve(_host: str, _port: int) -> list[str]:
        return ["203.0.113.10"]

    monkeypatch.setattr(net, "_resolve", _resolve)
    route = respx.get("https://203.0.113.10/info/v2/status").mock(return_value=httpx.Response(204))

    async with httpx.AsyncClient(follow_redirects=False) as client:
        response, final_url = await net.safe_request(
            client, "GET", "https://api.discover.swiss/info/v2/status"
        )

    assert response.status_code == 204
    assert final_url == "https://api.discover.swiss/info/v2/status"
    assert route.calls.last.request.headers["Host"] == "api.discover.swiss"


@respx.mock
async def test_a_redirect_off_the_allow_list_is_stopped(monkeypatch) -> None:
    async def _resolve(_host: str, _port: int) -> list[str]:
        return ["203.0.113.10"]

    monkeypatch.setattr(net, "_resolve", _resolve)
    respx.get("https://203.0.113.10/info/v2/status").mock(
        return_value=httpx.Response(302, headers={"location": "https://evil.example/steal"})
    )

    async with httpx.AsyncClient(follow_redirects=False) as client:
        with pytest.raises(net.EgressError):
            await net.safe_request(client, "GET", "https://api.discover.swiss/info/v2/status")


@respx.mock
async def test_a_post_is_never_replayed_at_a_redirect_target(monkeypatch) -> None:
    """The body carries the subscription-scoped query; a new target does not get it."""

    async def _resolve(_host: str, _port: int) -> list[str]:
        return ["203.0.113.10"]

    monkeypatch.setattr(net, "_resolve", _resolve)
    respx.post("https://203.0.113.10/info/v2/search").mock(
        return_value=httpx.Response(307, headers={"location": "/info/v2/elsewhere"})
    )

    async with httpx.AsyncClient(follow_redirects=False) as client:
        with pytest.raises(net.EgressError) as excinfo:
            await net.safe_request(
                client,
                "POST",
                "https://api.discover.swiss/info/v2/search",
                json_body={"project": ["dsod-content"]},
            )
    assert "redirect" in str(excinfo.value)
