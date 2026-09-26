"""The HTTP transport, assembled in one place and refused when unsafe.

Three rules, all decided at start-up so a misconfiguration never becomes a
running server:

1. **Loopback is the default and needs nothing.** Bound to ``127.0.0.1``,
   ``localhost`` or ``::1``, the server answers only under that name **and
   port** (``127.0.0.1:8000``, not ``127.0.0.1:*``). The SDK's own loopback
   default accepted any port (audit SEC-024).
2. **Any other bind address needs inbound OAuth and an explicit host list.**
   A server reachable from the network without authentication spends the
   operator's discover.swiss key for whoever finds the port (audit SEC-002,
   SEC-016). Refused, not warned about; and when it is allowed, the start
   is logged as a warning so it shows up in any log review.
3. **Host and Origin checks are always on**, with the lists passed
   explicitly to the SDK rather than left to its bind-address heuristic.

The app itself is the SDK's streamable-HTTP app. :class:`auth.ScopeGate`
wraps it when OAuth is configured.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from mcp.server.transport_security import TransportSecuritySettings

from discover_swiss_mcp.auth import AuthConfig, IntrospectionVerifier, ScopeGate
from discover_swiss_mcp.config import ConfigError, Settings
from discover_swiss_mcp.logging_config import get_logger

logger = get_logger("discover_swiss_mcp.http")

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def is_loopback(host: str) -> bool:
    return host in LOOPBACK_HOSTS


def transport_security(settings: Settings) -> TransportSecuritySettings:
    """Port-exact Host and Origin allow-lists, always enabled."""
    port = settings.port
    if settings.allowed_hosts:
        hosts = list(settings.allowed_hosts)
    else:
        hosts = [f"127.0.0.1:{port}", f"localhost:{port}", f"[::1]:{port}"]
    if settings.allowed_origins:
        origins = list(settings.allowed_origins)
    elif settings.allowed_hosts:
        # A request without Origin (a non-browser client) is still accepted by
        # the SDK; a browser origin must be named explicitly.
        origins = []
    else:
        origins = [f"http://127.0.0.1:{port}", f"http://localhost:{port}", f"http://[::1]:{port}"]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


def check_bind_policy(settings: Settings) -> None:
    """Raise :class:`ConfigError` for a bind address the server must not serve."""
    if is_loopback(settings.host):
        return
    missing: list[str] = []
    if not settings.auth_enabled:
        missing.append("inbound OAuth (DISCOVER_SWISS_MCP_AUTH_*)")
    if not settings.allowed_hosts:
        missing.append("DISCOVER_SWISS_MCP_ALLOWED_HOSTS (the exact Host values clients send)")
    if missing:
        raise ConfigError(
            f"Refusing to bind the HTTP transport to {settings.host!r}: a non-loopback "
            "address exposes the server — and the discover.swiss key behind it — to the "
            "network. Configure " + " and ".join(missing) + ", or bind to 127.0.0.1."
        )


def build_http_app(mcp_server: Any, settings: Settings) -> tuple[Any, IntrospectionVerifier | None]:
    """The ASGI app for uvicorn, plus the verifier to close on shutdown."""
    check_bind_policy(settings)
    security = transport_security(settings)
    app = mcp_server.streamable_http_app(host=settings.host, transport_security=security)

    if not is_loopback(settings.host):
        logger.warning(
            "http_bind_non_loopback",
            host=settings.host,
            port=settings.port,
            allowed_hosts=security.allowed_hosts,
            auth="oauth",
        )

    config = AuthConfig.from_settings(settings)
    if config is None:
        return app, None
    config = dataclasses.replace(config, allowed_hosts=tuple(security.allowed_hosts))
    verifier = IntrospectionVerifier(config)
    logger.info(
        "oauth_resource_server",
        resource=config.resource_url,
        issuer=config.issuer,
        metadata=config.metadata_url,
    )
    return ScopeGate(app, config, verifier), verifier
