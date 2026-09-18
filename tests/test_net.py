"""Outbound hardening: allow-list, IP block, DNS pinning, redirect gate."""

from __future__ import annotations

import httpx
import pytest
import respx

from discover_swiss_mcp import net


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


async def test_a_host_that_resolves_to_nothing_is_an_error(monkeypatch) -> None:
    async def _resolve(_host: str, _port: int) -> list[str]:
        return []

    monkeypatch.setattr(net, "_resolve", _resolve)
    with pytest.raises(net.EgressError):
        await net.assert_url_allowed("https://api.discover.swiss/info/v2/status")


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
