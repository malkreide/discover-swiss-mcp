"""Runtime configuration, read from environment variables.

Every field maps to exactly one environment variable, all of them prefixed
``DISCOVER_SWISS_``. Nothing is read from a file: the subscription key is a
bring-your-own-key secret and must never end up in a committed config.

**The key is never logged.** It is held as a ``SecretStr``, so an accidental
``repr()``, an f-string, a ``model_dump()`` or a structlog event renders
``**********`` instead of the value. Only :meth:`Settings.auth_header` unwraps
it, and only into the outbound HTTP header. The OAuth client secret for token
introspection is held the same way.

**Ingress lists come from the environment, egress lists do not.** The names a
deployment is reached under (``DISCOVER_SWISS_MCP_ALLOWED_HOSTS``) depend on
its domain and proxy and cannot be known in code; the host this server may
*call* is a ``frozenset`` in :mod:`discover_swiss_mcp.net` and changes only by
review. The one egress exception — the introspection endpoint of the
operator's authorization server — is read once at start-up and frozen.
"""

from __future__ import annotations

import os
from datetime import date
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, SecretStr

# PROD base of the Infocenter V2 API, as probed on 2026-09-17
# (spec Infocenter-PROD-V2 20260910.2_release).
API_BASE_URL = "https://api.discover.swiss/info/v2"

# The header the API gateway authenticates on. Named here rather than in the
# client so the one place that touches the secret is easy to find.
AUTH_HEADER = "Ocp-Apim-Subscription-Key"

# `dsod-content` is the superset of the open index; `dsod-hs` is the
# HotellerieSuisse subset and adds nothing. Sending the project explicitly is
# not optional: `/search` answers 401 without it, and the list endpoints fall
# back to an undocumented partner default.
DEFAULT_PROJECT = "dsod-content"


class ConfigError(RuntimeError):
    """Raised when the environment cannot produce a usable configuration."""


class Settings(BaseModel):
    """Configuration for one server process."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    api_key: SecretStr
    project: str = DEFAULT_PROJECT
    base_url: str = API_BASE_URL
    transport: Literal["stdio", "streamable-http"] = "stdio"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = "INFO"
    # Date on which discover.swiss confirmed in writing that the Open product
    # may use `/search`, or None while that is still pending. The probe
    # measured the access; the documentation denies it. `source_status` reports
    # which of the two a deployment is standing on.
    entitlement_confirmed: date | None = None
    # Ingress, HTTP transport only. Exact `host:port` values the server
    # answers to, and the origins it accepts. Empty means: derived from a
    # loopback bind (`127.0.0.1:<port>`, `localhost:<port>`, `[::1]:<port>`);
    # a non-loopback bind must name them.
    allowed_hosts: tuple[str, ...] = ()
    allowed_origins: tuple[str, ...] = ()
    # Inbound OAuth (resource server role), HTTP transport only. All five or
    # none: `auth_enabled` is true only when every one is set.
    auth_issuer: str | None = None
    auth_resource_url: str | None = None
    auth_introspection_url: str | None = None
    auth_client_id: str | None = None
    auth_client_secret: SecretStr | None = None

    @property
    def auth_enabled(self) -> bool:
        return self.auth_issuer is not None

    @property
    def auth_header(self) -> dict[str, str]:
        """The single place where the secret is unwrapped."""
        return {AUTH_HEADER: self.api_key.get_secret_value()}

    def safe_summary(self) -> dict[str, str | int]:
        """Everything about this configuration that is safe to log."""
        return {
            "project": self.project,
            "base_url": self.base_url,
            "transport": self.transport,
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "entitlement_confirmed": (
                self.entitlement_confirmed.isoformat() if self.entitlement_confirmed else "pending"
            ),
            "api_key": "set" if self.api_key.get_secret_value() else "missing",
            "auth": "oauth" if self.auth_enabled else "none",
        }


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else value


def load_settings(require_key: bool = True) -> Settings:
    """Build :class:`Settings` from the environment.

    ``require_key=False`` is for start-up paths that must work without a key —
    ``--help``, a health probe, the import-time smoke test. Everything that
    actually calls the API requires one.
    """
    raw_key = _env("DISCOVER_SWISS_KEY", "") or ""
    if require_key and not raw_key:
        raise ConfigError(
            "DISCOVER_SWISS_KEY is not set. The discover.swiss Infocenter Open is "
            "bring-your-own-key: create a subscription at portal.discover.swiss and "
            "export the key. Never put it in a file that gets committed."
        )

    port_raw = _env("DISCOVER_SWISS_MCP_PORT", "8000") or "8000"
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ConfigError(f"DISCOVER_SWISS_MCP_PORT is not a number: {port_raw!r}") from exc

    transport = (_env("DISCOVER_SWISS_MCP_TRANSPORT", "stdio") or "stdio").lower()
    if transport not in ("stdio", "streamable-http"):
        raise ConfigError(
            f"DISCOVER_SWISS_MCP_TRANSPORT is {transport!r}; expected 'stdio' or 'streamable-http'."
        )

    confirmed_raw = _env("DISCOVER_SWISS_ENTITLEMENT_CONFIRMED", "") or ""
    confirmed: date | None = None
    if confirmed_raw and confirmed_raw.lower() != "pending":
        # Loud rather than lenient: a typo here would silently report «pending»
        # on a deployment that believes it has the confirmation on record.
        try:
            confirmed = date.fromisoformat(confirmed_raw)
        except ValueError as exc:
            raise ConfigError(
                "DISCOVER_SWISS_ENTITLEMENT_CONFIRMED must be a date (YYYY-MM-DD) or "
                f"'pending', not {confirmed_raw!r}."
            ) from exc

    allowed_hosts = _split_list("DISCOVER_SWISS_MCP_ALLOWED_HOSTS")
    allowed_origins = _split_list("DISCOVER_SWISS_MCP_ALLOWED_ORIGINS")
    for host in allowed_hosts:
        # Exact values only. A name without a port is exact too: it is what a
        # client sends for the scheme's default port (`Host: mcp.example.ch`
        # behind an HTTPS ingress). Wildcards are refused — the SDK's loopback
        # default `127.0.0.1:*` accepted any port (audit SEC-024).
        if "*" in host:
            raise ConfigError(
                f"DISCOVER_SWISS_MCP_ALLOWED_HOSTS entry {host!r} contains a wildcard; list the "
                "exact Host values instead (mcp.example.ch, or mcp.example.ch:8443)."
            )

    auth = _load_auth()

    return Settings(
        api_key=SecretStr(raw_key),
        project=_env("DISCOVER_SWISS_PROJECT", DEFAULT_PROJECT) or DEFAULT_PROJECT,
        base_url=_env("DISCOVER_SWISS_BASE_URL", API_BASE_URL) or API_BASE_URL,
        transport=transport,  # type: ignore[arg-type]
        host=_env("DISCOVER_SWISS_MCP_HOST", "127.0.0.1") or "127.0.0.1",
        port=port,
        log_level=(_env("DISCOVER_SWISS_MCP_LOG_LEVEL", "INFO") or "INFO").upper(),
        entitlement_confirmed=confirmed,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
        **auth,
    )


def _split_list(name: str) -> tuple[str, ...]:
    raw = _env(name, "") or ""
    return tuple(item.strip() for item in raw.split(",") if item.strip())


AUTH_VARIABLES = {
    "auth_issuer": "DISCOVER_SWISS_MCP_AUTH_ISSUER",
    "auth_resource_url": "DISCOVER_SWISS_MCP_AUTH_RESOURCE_URL",
    "auth_introspection_url": "DISCOVER_SWISS_MCP_AUTH_INTROSPECTION_URL",
    "auth_client_id": "DISCOVER_SWISS_MCP_AUTH_CLIENT_ID",
    "auth_client_secret": "DISCOVER_SWISS_MCP_AUTH_CLIENT_SECRET",
}


def _load_auth() -> dict[str, object]:
    """All five OAuth variables, or none. Half a configuration is an error.

    A partly configured resource server is the dangerous case: it looks
    protected in the environment and is not. It fails loudly at start-up.
    """
    values = {field: _env(env, "") or "" for field, env in AUTH_VARIABLES.items()}
    present = [AUTH_VARIABLES[f] for f, v in values.items() if v]
    if not present:
        return {}
    missing = [AUTH_VARIABLES[f] for f, v in values.items() if not v]
    if missing:
        raise ConfigError(
            "Inbound OAuth is configured only in part; also set: " + ", ".join(missing) + "."
        )
    for field in ("auth_issuer", "auth_resource_url", "auth_introspection_url"):
        parsed = urlparse(values[field])
        if parsed.scheme != "https" or not parsed.hostname:
            raise ConfigError(
                f"{AUTH_VARIABLES[field]} must be an https:// URL, not {values[field]!r}."
            )
    return {
        "auth_issuer": values["auth_issuer"],
        "auth_resource_url": values["auth_resource_url"],
        "auth_introspection_url": values["auth_introspection_url"],
        "auth_client_id": values["auth_client_id"],
        "auth_client_secret": SecretStr(values["auth_client_secret"]),
    }
