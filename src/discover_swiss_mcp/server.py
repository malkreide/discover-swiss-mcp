"""discover-swiss MCP Server — scaffold (P0).

Swiss tourism data from the discover.swiss Infocenter Open: accommodation
nationwide, points of interest for Zurich, Eastern Switzerland and
Liechtenstein, tours, webcams and events, each hit carrying its own licence and
attribution.

This module currently registers **no tools**. P0 is structure, metadata and
CI; the eight tools of section 7 of the probe report land in P1. The empty
tool list is asserted by `tests/test_smoke.py`, so the first tool to appear
does so on purpose.

Transport: stdio (local) and streamable-http (cloud), selected by
``DISCOVER_SWISS_MCP_TRANSPORT``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.caching import CacheHint
from mcp.server.mcpserver import MCPServer

from discover_swiss_mcp.client import DiscoverSwissClient
from discover_swiss_mcp.config import ConfigError, Settings, load_settings
from discover_swiss_mcp.logging_config import configure_logging, get_logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The MCP protocol revision this server is built and tested against. Variant A
# of the SDK (`mcp>=2,<3`) negotiates this revision; a test holds the constant
# against the SDK's own `LATEST_PROTOCOL_VERSION` from P1 on, so the next drift
# is a failing build rather than a line nobody re-reads.
MCP_PROTOCOL_VERSION = "2026-07-28"

# SEP-2549: the listing methods carry `ttlMs` and `cacheScope`, and the SDK
# defaults both to "stale immediately, never shared". `public` follows from the
# facts: tools are registered by decorator at import time and there is no
# per-caller filtering. The moment a listing depends on the caller, the scope
# moves to `private` in the same commit.
LIST_CACHE_TTL_MS = 300_000

CACHE_HINTS = {
    "tools/list": CacheHint(ttl_ms=LIST_CACHE_TTL_MS, scope="public"),
    "server/discover": CacheHint(ttl_ms=LIST_CACHE_TTL_MS, scope="public"),
}

logger = get_logger("discover_swiss_mcp")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@dataclass
class AppContext:
    """Server-wide resources shared across tool calls."""

    settings: Settings | None = None
    client: DiscoverSwissClient | None = None


@asynccontextmanager
async def app_lifespan(server: MCPServer) -> AsyncIterator[AppContext]:
    """Manage server-wide resources across the whole lifecycle.

    The shared ``DiscoverSwissClient`` is created here and closed in the
    ``finally`` block — one client per process, not one per tool call. Its rate
    budget and its cache only mean anything if every tool call goes through the
    same instance; a client per call would hand each caller a fresh 55-per-
    minute allowance against a gateway that counts 60 for all of them together.

    Settings are loaded without requiring the key: a server that cannot even
    start without a subscription key cannot report its own configuration, and
    `source_status` has to be able to say "no key" rather than crash.
    """
    try:
        settings: Settings | None = load_settings(require_key=False)
    except ConfigError as exc:
        # Configuration problems are reported, not swallowed — but they must
        # not stop the process before it can say what is wrong.
        logger.error("settings_invalid", error=str(exc))
        settings = None

    client = DiscoverSwissClient(settings) if settings is not None else None

    # The structlog event the CI smoke test looks for. Never carries the key:
    # `safe_summary()` is the only view of Settings that gets logged.
    logger.info(
        "Server lifespan started",
        protocol_version=MCP_PROTOCOL_VERSION,
        tools=0,
        **(settings.safe_summary() if settings else {"config": "invalid"}),
    )
    try:
        yield AppContext(settings=settings, client=client)
    finally:
        if client is not None:
            await client.aclose()
        logger.info("Server lifespan stopped")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = MCPServer(
    "discover_swiss_mcp",
    cache_hints=CACHE_HINTS,
    instructions=(
        "MCP server for the discover.swiss Infocenter Open index (Swiss tourism "
        "data). Coverage is uneven and that matters for how you use it: "
        "accommodation is nationwide, points of interest are regional (Zurich, "
        "Eastern Switzerland, Liechtenstein, Engadin Scuol), and events are "
        "nearly empty. Every hit carries its own provider, licence and copyright "
        "notice — quote them. SCAFFOLD: this server registers no tools yet."
    ),
    lifespan=app_lifespan,
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
#
# None yet. P1 registers the eight read-only tools of the probe report,
# section 7 — `search`, `get_details`, `find_accommodation`, `find_tours`,
# `find_events`, `webcams_near`, `explore_area`, `source_status` — each with
# `readOnlyHint: true` and `openWorldHint: true`, and each split into a
# testable `*_impl` function separate from the MCP wrapper.


def main() -> None:
    """Start the server on the transport named by the environment."""
    settings = load_settings(require_key=False)
    # JSON logging to stderr; stdout belongs to the JSON-RPC stream.
    configure_logging(settings.log_level)

    if settings.transport == "streamable-http":
        import uvicorn

        # The bind address has to travel into the app: mcp 2.x derives its host
        # allow-list from it, and a default of 127.0.0.1 rejects every real
        # request with 421.
        uvicorn.run(
            mcp.streamable_http_app(host=settings.host),
            host=settings.host,
            port=settings.port,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
