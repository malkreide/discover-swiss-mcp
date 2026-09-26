"""Inbound OAuth: scope hierarchy, challenges, token introspection (audit SEC-003, SEC-002)."""

from __future__ import annotations

import base64
import json
import time
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import respx
from conftest import PINNED_IP
from mcp.server.auth.provider import AccessToken

from discover_swiss_mcp import auth
from discover_swiss_mcp.auth import (
    AuthConfig,
    IntrospectionUnavailableError,
    IntrospectionVerifier,
    Scope,
    ScopeGate,
    required_scopes,
)
from discover_swiss_mcp.server import mcp

CONFIG = AuthConfig(
    issuer="https://login.example.ch/realms/mcp",
    resource_url="https://mcp.example.ch/mcp",
    introspection_url="https://login.example.ch/realms/mcp/introspect",
    client_id="discover-swiss-mcp",
    client_secret="s3cret",
)
PINNED_INTROSPECT = f"https://{PINNED_IP}/realms/mcp/introspect"

BASIC = [Scope.TOOLS_BASIC.value]
READ = [Scope.TOOLS_BASIC.value, Scope.READ_PUBLIC.value]


def _call(name: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name}}


# ---------------------------------------------------------------------------
# The hierarchy
# ---------------------------------------------------------------------------


async def test_every_registered_tool_has_its_scopes() -> None:
    """A new tool without an entry would fall to the fail-closed default."""
    registered = {tool.name for tool in await mcp.list_tools()}
    assert registered == set(auth.TOOL_SCOPES)


def test_only_status_is_reachable_with_the_entry_scope() -> None:
    basic_only = {name for name, s in auth.TOOL_SCOPES.items() if s == auth.BASE_SCOPES}
    assert basic_only == {"source_status"}


def test_there_is_no_write_and_no_admin_scope() -> None:
    """Read-only server: a write or admin scope would promise an operation that does not exist."""
    values = [scope.value for scope in Scope]
    assert not [v for v in values if ":write" in v or v.startswith("admin")]
    assert all(Scope.READ_PUBLIC in s or s == auth.BASE_SCOPES for s in auth.TOOL_SCOPES.values())


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ({"jsonrpc": "2.0", "id": 1, "method": "initialize"}, BASIC),
        ({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, BASIC),
        (_call("source_status"), BASIC),
        (_call("search"), READ),
        (_call("no_such_tool"), READ),  # fail closed
        ({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {}}, READ),
        ([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, _call("get_details")], READ),
        (None, BASIC),
    ],
)
def test_required_scopes_per_message(message: Any, expected: list[str]) -> None:
    assert sorted(s.value for s in required_scopes(message)) == sorted(expected)


def test_metadata_names_the_whole_hierarchy_not_only_the_entry_scope() -> None:
    document = CONFIG.metadata()
    assert document["resource"] == CONFIG.resource_url
    assert document["authorization_servers"] == [CONFIG.issuer]
    assert document["scopes_supported"] == [s.value for s in Scope]
    assert CONFIG.metadata_url == "https://mcp.example.ch/.well-known/oauth-protected-resource/mcp"
    assert CONFIG.metadata_paths == (
        "/.well-known/oauth-protected-resource/mcp",
        "/.well-known/oauth-protected-resource",
    )


# ---------------------------------------------------------------------------
# The ASGI gate
# ---------------------------------------------------------------------------


class FakeVerifier:
    def __init__(self, tokens: dict[str, list[str]]) -> None:
        self.tokens = tokens

    async def verify_token(self, token: str) -> AccessToken | None:
        scopes = self.tokens.get(token)
        if scopes is None:
            return None
        return AccessToken(token=token, client_id="client", scopes=scopes)


class Recorder:
    """Stands in for the MCP app and records what reached it."""

    def __init__(self) -> None:
        self.bodies: list[bytes] = []

    async def __call__(self, scope, receive, send) -> None:
        chunks = []
        while True:
            message = await receive()
            chunks.append(message.get("body", b""))
            if not message.get("more_body"):
                break
        self.bodies.append(b"".join(chunks))
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})


def _gate(max_body: int = 1_000_000) -> tuple[httpx.AsyncClient, Recorder]:
    downstream = Recorder()
    gate = ScopeGate(
        downstream,
        CONFIG,
        FakeVerifier({"basic": BASIC, "reader": READ}),
        max_body_size=max_body,
    )
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=gate), base_url="http://mcp")
    return client, downstream


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_metadata_is_served_without_a_token() -> None:
    client, downstream = _gate()
    async with client:
        for path in CONFIG.metadata_paths:
            response = await client.get(path)
            assert response.status_code == 200
            assert response.json()["scopes_supported"] == [s.value for s in Scope]
    assert downstream.bodies == []


async def test_no_token_is_401_with_the_metadata_url() -> None:
    client, downstream = _gate()
    async with client:
        response = await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
    assert response.status_code == 401
    challenge = response.headers["www-authenticate"]
    assert challenge.startswith("Bearer ")
    assert f'resource_metadata="{CONFIG.metadata_url}"' in challenge
    assert 'scope="mcp:tools-basic"' in challenge
    assert downstream.bodies == []


async def test_an_unknown_token_is_401_invalid_token() -> None:
    client, downstream = _gate()
    async with client:
        response = await client.post("/mcp", json=_call("search"), headers=_bearer("forged"))
    assert response.status_code == 401
    assert 'error="invalid_token"' in response.headers["www-authenticate"]
    assert downstream.bodies == []


async def test_too_few_scopes_is_403_naming_the_missing_scope() -> None:
    client, downstream = _gate()
    async with client:
        response = await client.post("/mcp", json=_call("search"), headers=_bearer("basic"))
    assert response.status_code == 403
    challenge = response.headers["www-authenticate"]
    assert 'error="insufficient_scope"' in challenge
    assert "tourism:read:public" in challenge
    assert response.json()["error"] == "insufficient_scope"
    assert downstream.bodies == []


async def test_the_entry_scope_reaches_listing_and_status() -> None:
    client, downstream = _gate()
    body = json.dumps(_call("source_status")).encode()
    async with client:
        listing = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers=_bearer("basic"),
        )
        status = await client.post("/mcp", content=body, headers=_bearer("basic"))
    assert listing.status_code == 200
    assert status.status_code == 200
    # The body reaches the MCP app byte for byte.
    assert downstream.bodies[-1] == body


async def test_the_read_scope_reaches_the_data_tools() -> None:
    client, downstream = _gate()
    async with client:
        response = await client.post("/mcp", json=_call("search"), headers=_bearer("reader"))
    assert response.status_code == 200
    assert json.loads(downstream.bodies[-1])["params"]["name"] == "search"


async def test_a_body_over_the_limit_is_refused_before_the_app() -> None:
    client, downstream = _gate(max_body=64)
    async with client:
        response = await client.post(
            "/mcp",
            content=b"x" * 65,
            headers={**_bearer("reader"), "content-type": "application/json"},
        )
    assert response.status_code == 413
    assert downstream.bodies == []


class DownVerifier:
    async def verify_token(self, token: str) -> AccessToken | None:
        raise IntrospectionUnavailableError("down")


async def test_an_authorization_server_outage_is_503_not_invalid_token() -> None:
    downstream = Recorder()
    gate = ScopeGate(downstream, CONFIG, DownVerifier())
    transport = httpx.ASGITransport(app=gate)
    async with httpx.AsyncClient(transport=transport, base_url="http://mcp") as client:
        response = await client.post("/mcp", json=_call("search"), headers=_bearer("reader"))
    assert response.status_code == 503
    assert response.json()["error"] == "temporarily_unavailable"
    assert response.headers["retry-after"] == "10"
    assert "www-authenticate" not in response.headers
    assert downstream.bodies == []


@pytest.mark.parametrize("path", ["/.well-known/oauth-protected-resource/mcp", "/mcp"])
async def test_a_foreign_host_is_refused_before_metadata_or_token(path: str) -> None:
    """The metadata document follows the same Host rule as the MCP endpoint."""
    downstream = Recorder()
    config = AuthConfig(**{**CONFIG.__dict__, "allowed_hosts": ("mcp.example.ch",)})
    gate = ScopeGate(downstream, config, FakeVerifier({"reader": READ}))
    transport = httpx.ASGITransport(app=gate)
    async with httpx.AsyncClient(transport=transport, base_url="http://evil.example") as client:
        foreign = await client.get(path, headers=_bearer("reader"))
    async with httpx.AsyncClient(transport=transport, base_url="http://mcp.example.ch") as client:
        own = await client.get(path, headers=_bearer("reader"))
    assert foreign.status_code == 421
    assert own.status_code == 200
    assert len(downstream.bodies) == (1 if path == "/mcp" else 0)


# ---------------------------------------------------------------------------
# Token introspection (RFC 7662)
# ---------------------------------------------------------------------------


def _introspection(**overrides: Any) -> dict[str, Any]:
    answer = {
        "active": True,
        "scope": "mcp:tools-basic tourism:read:public",
        "client_id": "claude",
        "sub": "user-1",
        "iss": CONFIG.issuer,
        "aud": ["account", CONFIG.resource_url],
        "exp": int(time.time()) + 300,
    }
    answer.update(overrides)
    return {k: v for k, v in answer.items() if v is not None}


@respx.mock
async def test_an_active_token_for_this_resource_is_accepted() -> None:
    route = respx.post(PINNED_INTROSPECT).mock(
        return_value=httpx.Response(200, json=_introspection())
    )
    verifier = IntrospectionVerifier(CONFIG)
    try:
        token = await verifier.verify_token("abc")
    finally:
        await verifier.aclose()
    assert token is not None
    assert token.scopes == READ
    assert token.resource == CONFIG.resource_url
    request = route.calls.last.request
    assert parse_qs(request.content.decode())["token"] == ["abc"]
    expected = base64.b64encode(b"discover-swiss-mcp:s3cret").decode()
    assert request.headers["authorization"] == f"Basic {expected}"
    assert request.headers["host"] == "login.example.ch"


@pytest.mark.parametrize(
    "overrides",
    [
        {"active": False},
        {"aud": "https://other-service.example.ch/mcp"},  # issued for another resource
        {"aud": None},  # no audience at all
        {"iss": "https://evil.example/realms/mcp"},
        {"exp": int(time.time()) - 1},
    ],
)
@respx.mock
async def test_tokens_not_for_this_resource_are_refused(overrides: dict[str, Any]) -> None:
    respx.post(PINNED_INTROSPECT).mock(
        return_value=httpx.Response(200, json=_introspection(**overrides))
    )
    verifier = IntrospectionVerifier(CONFIG)
    try:
        assert await verifier.verify_token("abc") is None
    finally:
        await verifier.aclose()


@pytest.mark.parametrize(
    "outage",
    [
        httpx.Response(503),
        httpx.Response(200, text="<html>maintenance</html>"),
        httpx.ConnectError("refused"),
    ],
)
@respx.mock
async def test_an_unreachable_authorization_server_lets_nothing_through(outage) -> None:
    """No verdict is not «invalid»: it raises, so the gate can answer 503."""
    if isinstance(outage, Exception):
        respx.post(PINNED_INTROSPECT).mock(side_effect=outage)
    else:
        respx.post(PINNED_INTROSPECT).mock(return_value=outage)
    verifier = IntrospectionVerifier(CONFIG)
    try:
        with pytest.raises(IntrospectionUnavailableError):
            await verifier.verify_token("abc")
    finally:
        await verifier.aclose()


@respx.mock
async def test_an_outage_is_not_cached_so_a_valid_token_works_after_recovery() -> None:
    """Re-verification of SEC-002: an outage cached as «invalid» locked a valid token out."""
    route = respx.post(PINNED_INTROSPECT).mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json=_introspection())]
    )
    verifier = IntrospectionVerifier(CONFIG)
    try:
        with pytest.raises(IntrospectionUnavailableError):
            await verifier.verify_token("abc")
        assert await verifier.verify_token("abc") is not None
    finally:
        await verifier.aclose()
    assert route.call_count == 2


@respx.mock
async def test_an_answer_without_issuer_is_refused() -> None:
    """`iss` is optional in RFC 7662 and required here."""
    answer = _introspection()
    del answer["iss"]
    respx.post(PINNED_INTROSPECT).mock(return_value=httpx.Response(200, json=answer))
    verifier = IntrospectionVerifier(CONFIG)
    try:
        assert await verifier.verify_token("abc") is None
    finally:
        await verifier.aclose()


def test_the_client_secret_is_not_in_the_config_repr() -> None:
    assert "s3cret" not in repr(CONFIG)
    assert "s3cret" not in str(CONFIG)


@respx.mock
async def test_an_answer_is_cached_briefly() -> None:
    route = respx.post(PINNED_INTROSPECT).mock(
        return_value=httpx.Response(200, json=_introspection())
    )
    verifier = IntrospectionVerifier(CONFIG)
    try:
        first = await verifier.verify_token("abc")
        second = await verifier.verify_token("abc")
    finally:
        await verifier.aclose()
    assert first == second
    assert route.call_count == 1


async def test_introspection_only_reaches_its_own_host(monkeypatch) -> None:
    """The one egress exception is exactly the configured host, nothing else."""
    other = AuthConfig(**{**CONFIG.__dict__, "introspection_url": "https://login.example.ch/x"})
    verifier = IntrospectionVerifier(other)
    try:
        assert verifier._allowlist == frozenset({"login.example.ch"})
    finally:
        await verifier.aclose()
