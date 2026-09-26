"""The HTTP transport: bind policy, port-exact Host/Origin checks, OAuth wiring.

Audit SEC-016 (a non-loopback bind was silent), SEC-024 (the Host allow-list
accepted any port and was never wired explicitly), SEC-003 (inbound OAuth).
These tests run the real SDK app through Starlette's TestClient, which also
runs the lifespan — the Host check lives inside the MCP endpoint, so a test
against a stand-in app would prove nothing about it.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from discover_swiss_mcp import http_app, server
from discover_swiss_mcp.auth import ScopeGate
from discover_swiss_mcp.config import ConfigError, load_settings
from discover_swiss_mcp.http_app import build_http_app, check_bind_policy, transport_security

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "ping",
}
HEADERS = {"accept": "application/json, text/event-stream", "content-type": "application/json"}

AUTH_ENV = {
    "DISCOVER_SWISS_MCP_AUTH_ISSUER": "https://login.example.ch/realms/mcp",
    "DISCOVER_SWISS_MCP_AUTH_RESOURCE_URL": "https://mcp.example.ch/mcp",
    "DISCOVER_SWISS_MCP_AUTH_INTROSPECTION_URL": "https://login.example.ch/realms/mcp/introspect",
    "DISCOVER_SWISS_MCP_AUTH_CLIENT_ID": "discover-swiss-mcp",
    "DISCOVER_SWISS_MCP_AUTH_CLIENT_SECRET": "s3cret",
}


def _settings(monkeypatch, **env: str):
    monkeypatch.setenv("DISCOVER_SWISS_MCP_TRANSPORT", "streamable-http")
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    return load_settings(require_key=False)


# ---------------------------------------------------------------------------
# Host and Origin (SEC-024)
# ---------------------------------------------------------------------------


def test_loopback_lists_are_port_exact(monkeypatch) -> None:
    security = transport_security(_settings(monkeypatch, DISCOVER_SWISS_MCP_PORT="8123"))
    assert security.enable_dns_rebinding_protection is True
    assert security.allowed_hosts == ["127.0.0.1:8123", "localhost:8123", "[::1]:8123"]
    assert not [h for h in security.allowed_hosts + security.allowed_origins if h.endswith(":*")]


@pytest.mark.parametrize(
    ("host", "origin", "rejected_with"),
    [
        ("127.0.0.1:9999", None, 421),  # right name, wrong port: the SDK default let this through
        ("evil.example:8000", None, 421),
        ("127.0.0.1:8000", "http://evil.example", 403),
    ],
)
def test_foreign_host_port_or_origin_is_refused(monkeypatch, host, origin, rejected_with) -> None:
    app, _ = build_http_app(server.mcp, _settings(monkeypatch))
    headers = {**HEADERS, "host": host}
    if origin:
        headers["origin"] = origin
    with TestClient(app) as client:
        response = client.post("/mcp", json=INIT, headers=headers)
    assert response.status_code == rejected_with


def test_the_configured_host_and_port_are_accepted(monkeypatch) -> None:
    """The counter-check: the exact name passes the Host check."""
    app, _ = build_http_app(server.mcp, _settings(monkeypatch))
    with TestClient(app) as client:
        response = client.post("/mcp", json=INIT, headers={**HEADERS, "host": "127.0.0.1:8000"})
    # Past the Host check, the protocol layer answers — with a JSON-RPC body,
    # not the transport's plain «Invalid Host header».
    assert response.status_code not in (403, 421)
    assert response.json()["jsonrpc"] == "2.0"


# ---------------------------------------------------------------------------
# Bind policy (SEC-016)
# ---------------------------------------------------------------------------


def test_a_network_bind_without_oauth_is_refused(monkeypatch) -> None:
    settings = _settings(
        monkeypatch,
        DISCOVER_SWISS_MCP_HOST="0.0.0.0",
        DISCOVER_SWISS_MCP_ALLOWED_HOSTS="mcp.example.ch:443",
    )
    with pytest.raises(ConfigError, match="inbound OAuth"):
        check_bind_policy(settings)


def test_a_network_bind_without_a_host_list_is_refused(monkeypatch) -> None:
    settings = _settings(monkeypatch, DISCOVER_SWISS_MCP_HOST="0.0.0.0", **AUTH_ENV)
    with pytest.raises(ConfigError, match="ALLOWED_HOSTS"):
        check_bind_policy(settings)


def test_main_stops_before_uvicorn_on_an_unsafe_bind(monkeypatch) -> None:
    started: list[object] = []
    monkeypatch.setattr("uvicorn.run", lambda *a, **k: started.append(a))
    monkeypatch.setenv("DISCOVER_SWISS_MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("DISCOVER_SWISS_MCP_HOST", "0.0.0.0")
    with pytest.raises(SystemExit) as excinfo:
        server.main()
    assert excinfo.value.code == 2
    assert started == []


def test_main_hands_the_checked_app_to_uvicorn(monkeypatch) -> None:
    """The seam main() → build_http_app → uvicorn (audit ARCH-013)."""
    started: list[tuple] = []
    monkeypatch.setattr("uvicorn.run", lambda app, **k: started.append((app, k)))
    monkeypatch.setenv("DISCOVER_SWISS_MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("DISCOVER_SWISS_MCP_PORT", "8124")
    server.main()
    ((app, kwargs),) = started
    assert kwargs == {"host": "127.0.0.1", "port": 8124}
    with TestClient(app) as client:
        wrong_port = client.post("/mcp", json=INIT, headers={**HEADERS, "host": "127.0.0.1:8000"})
    assert wrong_port.status_code == 421


def test_a_network_bind_is_logged_as_a_warning(monkeypatch) -> None:
    events: list[tuple[str, dict]] = []

    class _Log:
        def warning(self, event, **kw):
            events.append((event, kw))

        def info(self, event, **kw):
            pass

    monkeypatch.setattr(http_app, "logger", _Log())
    settings = _settings(
        monkeypatch,
        DISCOVER_SWISS_MCP_HOST="0.0.0.0",
        DISCOVER_SWISS_MCP_ALLOWED_HOSTS="mcp.example.ch:443",
        **AUTH_ENV,
    )
    app, verifier = build_http_app(server.mcp, settings)
    assert isinstance(app, ScopeGate)
    assert verifier is not None
    assert [e for e, _ in events] == ["http_bind_non_loopback"]


# ---------------------------------------------------------------------------
# OAuth wired into the real app (SEC-003)
# ---------------------------------------------------------------------------


def test_with_oauth_the_real_app_demands_a_token_and_serves_metadata(monkeypatch) -> None:
    settings = _settings(monkeypatch, **AUTH_ENV)
    app, _ = build_http_app(server.mcp, settings)
    with TestClient(app) as client:
        metadata = client.get(
            "/.well-known/oauth-protected-resource/mcp", headers={"host": "127.0.0.1:8000"}
        )
        foreign = client.get(
            "/.well-known/oauth-protected-resource/mcp", headers={"host": "evil.example"}
        )
        anonymous = client.post("/mcp", json=INIT, headers={**HEADERS, "host": "127.0.0.1:8000"})
    assert metadata.status_code == 200
    assert foreign.status_code == 421
    assert metadata.json()["scopes_supported"] == ["mcp:tools-basic", "tourism:read:public"]
    assert anonymous.status_code == 401
    assert "resource_metadata=" in anonymous.headers["www-authenticate"]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_half_an_oauth_configuration_is_an_error(monkeypatch) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_MCP_AUTH_ISSUER", AUTH_ENV["DISCOVER_SWISS_MCP_AUTH_ISSUER"])
    with pytest.raises(ConfigError, match="only in part"):
        load_settings(require_key=False)


def test_oauth_urls_must_be_https(monkeypatch) -> None:
    env = {**AUTH_ENV, "DISCOVER_SWISS_MCP_AUTH_INTROSPECTION_URL": "http://login.example.ch/x"}
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError, match="https"):
        load_settings(require_key=False)


@pytest.mark.parametrize("entry", ["https://*.example.ch", "*"])
def test_origin_entries_must_not_be_wildcards(monkeypatch, entry: str) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_MCP_ALLOWED_ORIGINS", entry)
    with pytest.raises(ConfigError, match="wildcard"):
        load_settings(require_key=False)


@pytest.mark.parametrize("entry", ["mcp.example.ch:*", "*.example.ch"])
def test_host_entries_must_not_be_wildcards(monkeypatch, entry: str) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_MCP_ALLOWED_HOSTS", entry)
    with pytest.raises(ConfigError, match="wildcard"):
        load_settings(require_key=False)


def test_a_name_without_port_is_exact_and_matches_an_ingress_host(monkeypatch) -> None:
    """Behind an HTTPS ingress the client sends `Host: mcp.example.ch`, no port."""
    settings = _settings(
        monkeypatch,
        DISCOVER_SWISS_MCP_HOST="0.0.0.0",
        DISCOVER_SWISS_MCP_ALLOWED_HOSTS="mcp.example.ch",
        **AUTH_ENV,
    )
    gate, _ = build_http_app(server.mcp, settings)
    inner = gate.app  # past the OAuth layer: the Host check alone
    with TestClient(inner) as client:
        ok = client.post("/mcp", json=INIT, headers={**HEADERS, "host": "mcp.example.ch"})
        other_port = client.post(
            "/mcp", json=INIT, headers={**HEADERS, "host": "mcp.example.ch:8443"}
        )
    assert ok.status_code != 421
    assert other_port.status_code == 421


def test_the_client_secret_never_appears_in_the_summary(monkeypatch) -> None:
    settings = _settings(monkeypatch, **AUTH_ENV)
    summary = settings.safe_summary()
    assert summary["auth"] == "oauth"
    assert "s3cret" not in repr(settings)
    assert "s3cret" not in str(summary)
