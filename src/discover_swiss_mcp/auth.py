"""Inbound OAuth for the HTTP transport: scopes, token check, challenges.

Off by default. stdio never sees any of this: a local process started by the
user's own MCP host has no caller to authenticate. On the HTTP transport it is
**required** as soon as the server binds to anything but loopback
(:mod:`discover_swiss_mcp.http_app`); on loopback it is optional.

The server is an OAuth *resource server* only. It issues no tokens and runs no
authorization flow; the operator's authorization server does that. What this
module does, in request order:

1. Serves the protected resource metadata (RFC 9728) under
   ``/.well-known/oauth-protected-resource`` and its path-suffixed form, naming
   the resource, the authorization server and **every** scope of the hierarchy
   below — not only the ones a first request needs.
2. Requires a bearer token on the MCP endpoint and checks it by token
   introspection (RFC 7662): active, not expired, issued by the configured
   issuer, and issued **for this resource** (``aud`` contains the resource URL,
   RFC 8707). A token for another service is refused even if it is valid there.
3. Checks the scopes the JSON-RPC request needs, per call: the body is read,
   the method and — for ``tools/call`` — the tool name decide. Not the routing
   headers alone: they are client-supplied, and the SDK checks them against the
   body only after this layer has let the request through.
4. Answers a missing or invalid token with 401, too few scopes with 403, both
   with ``WWW-Authenticate`` naming the scope and the metadata URL, so a client
   can ask for exactly the scope it lacks (progressive consent, SEP-835).

Why not the SDK's own auth wiring: it publishes ``required_scopes`` as
``scopes_supported``, which makes the metadata advertise only the entry scope
and hide the rest of the hierarchy (audit SEC-003, criterion 6). Token
verification still follows the SDK's ``AccessToken`` shape.

Why introspection and not local JWT validation: no new dependency, works with
opaque tokens as well as JWTs, and a revoked token stops working at once rather
than at its expiry. The cost — one call to the authorization server per token
and minute — is bounded by a short cache.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from urllib.parse import urlparse

import httpx
from mcp.server.auth.provider import AccessToken
from mcp.server.transport_security import DEFAULT_MAX_REQUEST_BODY_SIZE
from starlette.types import ASGIApp, Message, Receive, Send
from starlette.types import Scope as ASGIScope

from discover_swiss_mcp import net
from discover_swiss_mcp.config import Settings
from discover_swiss_mcp.logging_config import get_logger

logger = get_logger("discover_swiss_mcp.auth")

METADATA_PATH = "/.well-known/oauth-protected-resource"
REALM = "discover-swiss-mcp"

# How long an introspection answer is trusted. Short: a revoked token must stop
# working soon, and a minute of one extra call per token costs nothing.
INTROSPECTION_CACHE_SECONDS = 60.0
INTROSPECTION_CACHE_MAX = 1024
INTROSPECTION_TIMEOUT_SECONDS = 10.0


class Scope(StrEnum):
    """The scope hierarchy. Two dimensions: access (read/write) and data class.

    * ``mcp:tools-basic`` — discovery: initialise, list tools, ping, and
      ``source_status`` (the server's own health; no index content). The one
      scope a first authorisation needs.
    * ``tourism:read:public`` — every tool that returns index content. The data
      class is ``public`` because nothing else is ever served: objects under a
      non-open licence are withheld for every caller, so a scope that unlocked
      them would promise something the server does not do.

    There is **no write scope and no admin scope**, because there is no tool
    that writes and no administrative operation. A write tool would get
    ``tourism:write:<class>``; an admin operation an ``admin:<operation>``
    scope outside this hierarchy — never folded into the ones above.
    """

    TOOLS_BASIC = "mcp:tools-basic"
    READ_PUBLIC = "tourism:read:public"


# Scopes a tool call needs, per tool. A test holds that every registered tool
# has an entry: a new tool without one would fall to the fail-closed default.
TOOL_SCOPES: dict[str, frozenset[Scope]] = {
    "search": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "get_details": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "find_accommodation": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "find_tours": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "find_events": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "webcams_near": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "explore_area": frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC}),
    "source_status": frozenset({Scope.TOOLS_BASIC}),
}

# Every request needs at least this — the entry scope of the hierarchy.
BASE_SCOPES: frozenset[Scope] = frozenset({Scope.TOOLS_BASIC})

# A `tools/call` for a name not in TOOL_SCOPES: fail closed, ask for the most
# a read can need. The SDK then answers «unknown tool» — to an authorised caller.
UNKNOWN_TOOL_SCOPES: frozenset[Scope] = frozenset({Scope.TOOLS_BASIC, Scope.READ_PUBLIC})


def required_scopes(message: Any) -> frozenset[Scope]:
    """Scopes one JSON-RPC message (or a batch of them) needs."""
    if isinstance(message, list):
        needed: set[Scope] = set(BASE_SCOPES)
        for item in message:
            needed |= required_scopes(item)
        return frozenset(needed)
    if not isinstance(message, dict) or message.get("method") != "tools/call":
        return BASE_SCOPES
    params = message.get("params")
    name = params.get("name") if isinstance(params, dict) else None
    if not isinstance(name, str):
        return UNKNOWN_TOOL_SCOPES
    return TOOL_SCOPES.get(name, UNKNOWN_TOOL_SCOPES)


# ---------------------------------------------------------------------------
# Token verification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuthConfig:
    """The resource server's view of the operator's authorization server."""

    issuer: str
    resource_url: str
    introspection_url: str
    client_id: str
    # Out of the dataclass repr: a traceback or a debug print must not carry it.
    client_secret: str = field(repr=False)
    # The Host values the metadata document is served under — the same list
    # the MCP endpoint enforces. Empty: no check here (tests, loopback).
    allowed_hosts: tuple[str, ...] = ()

    @property
    def metadata_url(self) -> str:
        """RFC 9728 §3.1: the well-known segment goes between host and path."""
        parsed = urlparse(self.resource_url)
        path = parsed.path if parsed.path not in ("", "/") else ""
        return f"{parsed.scheme}://{parsed.netloc}{METADATA_PATH}{path}"

    @property
    def metadata_paths(self) -> tuple[str, ...]:
        parsed = urlparse(self.resource_url)
        path = parsed.path if parsed.path not in ("", "/") else ""
        return (METADATA_PATH + path, METADATA_PATH) if path else (METADATA_PATH,)

    def metadata(self) -> dict[str, Any]:
        return {
            "resource": self.resource_url,
            "authorization_servers": [self.issuer],
            "scopes_supported": [scope.value for scope in Scope],
            "bearer_methods_supported": ["header"],
            "resource_name": REALM,
        }

    @classmethod
    def from_settings(cls, settings: Settings) -> AuthConfig | None:
        if not settings.auth_enabled:
            return None
        assert settings.auth_client_secret is not None  # all five or none, see config
        return cls(
            issuer=str(settings.auth_issuer),
            resource_url=str(settings.auth_resource_url),
            introspection_url=str(settings.auth_introspection_url),
            client_id=str(settings.auth_client_id),
            client_secret=settings.auth_client_secret.get_secret_value(),
        )


class IntrospectionUnavailableError(Exception):
    """The authorization server could not answer: no verdict about the token.

    Kept apart from «invalid token» on purpose (audit re-verification of
    SEC-028/SEC-002): an outage answered as `invalid_token` sends a client
    into re-authorisation for nothing, and caching it locked out a valid token
    for a minute. It becomes a 503 and is never cached.
    """


class IntrospectionVerifier:
    """Checks a bearer token at the authorization server (RFC 7662).

    Returns an ``AccessToken`` only for a token that is active, unexpired,
    issued by the configured issuer and addressed to this resource. Everything
    else — including an authorization server that cannot be reached — is
    ``None``: a request is never let through because the check failed.
    """

    def __init__(self, config: AuthConfig, client: httpx.AsyncClient | None = None) -> None:
        self._config = config
        self._client = client or httpx.AsyncClient(
            timeout=INTROSPECTION_TIMEOUT_SECONDS, follow_redirects=False
        )
        # The one egress exception, fixed here and never extended at runtime.
        host = urlparse(config.introspection_url).hostname or ""
        self._allowlist: frozenset[str] = frozenset({host})
        self._cache: dict[str, tuple[float, AccessToken | None]] = {}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def verify_token(self, token: str) -> AccessToken | None:
        key = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = time.monotonic()
        cached = self._cache.get(key)
        if cached is not None and cached[0] > now:
            return cached[1]

        result = await self._introspect(token)  # raises on an outage; nothing cached
        expiry = now + INTROSPECTION_CACHE_SECONDS
        if result is not None and result.expires_at is not None:
            expiry = min(expiry, now + max(0.0, result.expires_at - time.time()))
        if len(self._cache) >= INTROSPECTION_CACHE_MAX:
            self._cache.clear()
        self._cache[key] = (expiry, result)
        return result

    async def _introspect(self, token: str) -> AccessToken | None:
        try:
            response, _ = await net.safe_request(
                self._client,
                "POST",
                self._config.introspection_url,
                form_body={"token": token, "token_type_hint": "access_token"},
                auth=(self._config.client_id, self._config.client_secret),
                allowlist=self._allowlist,
                headers={"Accept": "application/json"},
            )
        except net.EgressError as exc:
            # A policy block is a configuration error, not a transient one —
            # logged as such, and still no verdict about the token.
            logger.error("introspection_blocked", reason=str(exc))
            raise IntrospectionUnavailableError("introspection blocked by egress policy") from exc
        except httpx.HTTPError as exc:
            logger.error("introspection_unreachable", reason=type(exc).__name__)
            raise IntrospectionUnavailableError("authorization server unreachable") from exc
        if response.status_code != 200:
            logger.error("introspection_unreachable", status=response.status_code)
            raise IntrospectionUnavailableError(f"introspection answered {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:
            logger.error("introspection_unreachable", reason="not_json")
            raise IntrospectionUnavailableError("introspection answer is not JSON") from exc
        return self._access_token(token, data)

    def _access_token(self, token: str, data: Any) -> AccessToken | None:
        if not isinstance(data, dict) or data.get("active") is not True:
            return None
        exp = data.get("exp")
        if isinstance(exp, int | float) and exp <= time.time():
            return None
        # `iss` is optional in RFC 7662 but required here: without it, nothing
        # ties the answer to the one authorization server this resource trusts
        # (audit SEC-002, criterion 5).
        issuer = data.get("iss")
        if issuer is None or str(issuer).rstrip("/") != self._config.issuer.rstrip("/"):
            logger.warning("token_rejected", reason="issuer")
            return None
        # `aud` is required here (RFC 8707): without it, a token issued for any
        # other service of the same authorization server would be accepted.
        audience = data.get("aud")
        audiences = audience if isinstance(audience, list) else [audience]
        resource = self._config.resource_url.rstrip("/")
        if resource not in {str(a).rstrip("/") for a in audiences if a is not None}:
            logger.warning("token_rejected", reason="audience")
            return None
        scope = data.get("scope")
        scopes = scope.split() if isinstance(scope, str) else []
        return AccessToken(
            token=token,
            client_id=str(data.get("client_id") or ""),
            scopes=scopes,
            expires_at=int(exp) if isinstance(exp, int | float) else None,
            resource=self._config.resource_url,
            subject=str(data["sub"]) if data.get("sub") is not None else None,
            claims={"iss": issuer},
        )


# ---------------------------------------------------------------------------
# ASGI layer
# ---------------------------------------------------------------------------


class _BodyTooLarge(Exception):
    pass


class ScopeGate:
    """ASGI middleware in front of the MCP app: metadata, 401, 403.

    Everything except the metadata document requires a valid token. The
    request body is read once, bounded by the SDK's own limit, checked, and
    replayed unchanged to the MCP app.
    """

    def __init__(
        self,
        app: ASGIApp,
        config: AuthConfig,
        verifier: Any,
        max_body_size: int = DEFAULT_MAX_REQUEST_BODY_SIZE,
    ) -> None:
        self.app = app
        self.config = config
        self.verifier = verifier
        self.max_body_size = max_body_size

    async def __call__(self, scope: ASGIScope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self.config.allowed_hosts and _host(scope) not in self.config.allowed_hosts:
            # Same rule as the MCP endpoint, applied before anything is
            # answered — the metadata document included.
            await _json(send, 421, {"error": "invalid host"})
            return

        if scope["path"] in self.config.metadata_paths and scope["method"] == "GET":
            await _json(send, 200, self.config.metadata())
            return

        token = _bearer(scope)
        if token is None:
            await self._challenge(send, 401, error=None, needed=BASE_SCOPES)
            return
        try:
            access = await self.verifier.verify_token(token)
        except IntrospectionUnavailableError:
            await _json(
                send,
                503,
                {
                    "error": "temporarily_unavailable",
                    "error_description": "token check unavailable",
                },
                extra_headers=[(b"retry-after", b"10")],
            )
            return
        if access is None:
            await self._challenge(send, 401, error="invalid_token", needed=BASE_SCOPES)
            return

        body = b""
        message: Any = None
        if scope["method"] == "POST":
            try:
                body = await _read_body(receive, self.max_body_size)
            except _BodyTooLarge:
                await _json(send, 413, {"error": "request body too large"})
                return
            try:
                message = json.loads(body) if body else None
            except ValueError:
                message = None  # the MCP app answers the parse error itself

        needed = required_scopes(message)
        missing = sorted(s.value for s in needed if s.value not in access.scopes)
        if missing:
            logger.warning("insufficient_scope", missing=missing, client_id=access.client_id)
            await self._challenge(send, 403, error="insufficient_scope", needed=needed)
            return

        # Who called what — the caller's identity per call (audit SEC-002,
        # criterion 4). Never the token itself.
        logger.info(
            "authorized_call",
            client_id=access.client_id,
            subject=access.subject,
            method=message.get("method") if isinstance(message, dict) else None,
            tool=_tool_name(message),
        )
        await self.app(scope, _replay(body, receive), send)

    async def _challenge(
        self, send: Send, status: int, *, error: str | None, needed: frozenset[Scope]
    ) -> None:
        scope_value = " ".join(sorted(s.value for s in needed))
        parts = [f'Bearer realm="{REALM}"']
        if error:
            parts.append(f'error="{error}"')
        parts.append(f'scope="{scope_value}"')
        parts.append(f'resource_metadata="{self.config.metadata_url}"')
        body: dict[str, Any] = {"error": error or "unauthorized", "scope": scope_value}
        await _json(
            send, status, body, extra_headers=[(b"www-authenticate", ", ".join(parts).encode())]
        )


def _host(scope: ASGIScope) -> str | None:
    for name, value in scope.get("headers", []):
        if name == b"host":
            return value.decode("latin-1")
    return None


def _tool_name(message: Any) -> str | None:
    if isinstance(message, dict) and message.get("method") == "tools/call":
        params = message.get("params")
        name = params.get("name") if isinstance(params, dict) else None
        return name if isinstance(name, str) else None
    return None


def _bearer(scope: ASGIScope) -> str | None:
    for name, value in scope.get("headers", []):
        if name == b"authorization":
            text = value.decode("latin-1")
            kind, _, token = text.partition(" ")
            if kind.lower() == "bearer" and token.strip():
                return token.strip()
            return None
    return None


async def _read_body(receive: Receive, limit: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while True:
        message = await receive()
        if message["type"] != "http.request":
            break
        chunk = message.get("body", b"")
        size += len(chunk)
        if size > limit:
            raise _BodyTooLarge
        chunks.append(chunk)
        if not message.get("more_body", False):
            break
    return b"".join(chunks)


def _replay(body: bytes, receive: Receive) -> Receive:
    sent = False

    async def _receive() -> Message:
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()

    return _receive


async def _json(
    send: Send,
    status: int,
    payload: dict[str, Any],
    extra_headers: list[tuple[bytes, bytes]] | None = None,
) -> None:
    body = json.dumps(payload).encode("utf-8")
    headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(body)).encode()),
        (b"cache-control", b"no-store"),
        *(extra_headers or []),
    ]
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})
