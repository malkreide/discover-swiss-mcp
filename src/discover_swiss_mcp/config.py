"""Runtime configuration, read from environment variables.

Every field maps to exactly one environment variable, all of them prefixed
``DISCOVER_SWISS_``. Nothing is read from a file: the subscription key is a
bring-your-own-key secret and must never end up in a committed config.

**The key is never logged.** It is held as a ``SecretStr``, so an accidental
``repr()``, an f-string, a ``model_dump()`` or a structlog event renders
``**********`` instead of the value. Only :meth:`Settings.auth_header` unwraps
it, and only into the outbound HTTP header.
"""

from __future__ import annotations

import os
from datetime import date
from typing import Literal

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

    return Settings(
        api_key=SecretStr(raw_key),
        project=_env("DISCOVER_SWISS_PROJECT", DEFAULT_PROJECT) or DEFAULT_PROJECT,
        base_url=_env("DISCOVER_SWISS_BASE_URL", API_BASE_URL) or API_BASE_URL,
        transport=transport,  # type: ignore[arg-type]
        host=_env("DISCOVER_SWISS_MCP_HOST", "127.0.0.1") or "127.0.0.1",
        port=port,
        log_level=(_env("DISCOVER_SWISS_MCP_LOG_LEVEL", "INFO") or "INFO").upper(),
        entitlement_confirmed=confirmed,
    )
