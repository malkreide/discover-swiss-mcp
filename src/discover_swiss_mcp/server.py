"""discover-swiss MCP Server.

Swiss tourism data from the discover.swiss Infocenter Open: accommodation
nationwide, points of interest for Zurich, Eastern Switzerland and
Liechtenstein, tours, webcams and events, each hit carrying its own licence and
attribution.

The eight tools of section 7 of the probe report: ``search``,
``get_details``, ``find_accommodation``, ``find_tours`` (P2) and
``find_events``, ``webcams_near``, ``explore_area``, ``source_status`` (P3).
The logic lives in :mod:`discover_swiss_mcp.tools` as ``*_impl`` functions; this module
only adds the protocol layer: annotations, the description the model reads,
the shared client from the lifespan and the masking of errors.

Transport: stdio (local) and streamable-http (cloud), selected by
``DISCOVER_SWISS_MCP_TRANSPORT``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import NoReturn

from mcp.server.caching import CacheHint
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from discover_swiss_mcp import net
from discover_swiss_mcp._version import __version__
from discover_swiss_mcp.client import (
    AuthorizationError,
    DiscoverSwissClient,
    NotFoundError,
    UpstreamRejectedError,
)
from discover_swiss_mcp.config import ConfigError, Settings, load_settings
from discover_swiss_mcp.logging_config import configure_logging, get_logger, tool_logger
from discover_swiss_mcp.tools import (
    AccommodationResponse,
    DetailResponse,
    EventsResponse,
    ExploreAreaInput,
    ExploreAreaResponse,
    FindAccommodationInput,
    FindEventsInput,
    FindToursInput,
    GetDetailsInput,
    SearchInput,
    SearchResponse,
    SourceStatusResponse,
    ToursResponse,
    WebcamsNearInput,
    WebcamsResponse,
    explore_area_impl,
    find_accommodation_impl,
    find_events_impl,
    find_tours_impl,
    get_details_impl,
    search_impl,
    source_status_impl,
    webcams_near_impl,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The MCP protocol revision this server is built and tested against.
#
# What this constant does and does not do (audit ARCH-012): it is reported in
# the tool-hash snapshot and in the start-up log, and a test holds it equal to
# the SDK's `mcp_types.LATEST_PROTOCOL_VERSION` — an SDK update that moves the
# protocol fails the build instead of changing it silently. It does NOT decide
# negotiation: the SDK answers each request from its own list of supported
# revisions, and over HTTP it still serves the pre-2026 `initialize` handshake
# to legacy clients (audit ARCH-015, accepted until the SDK offers a switch).
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
        tools=len(await server.list_tools()),
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
    # serverInfo.version on the wire. The SDK default is "" (audit ARCH-016):
    # a client could not tell which release it is talking to.
    version=__version__,
    cache_hints=CACHE_HINTS,
    instructions=(
        "MCP server for the discover.swiss Infocenter Open index (Swiss tourism "
        "data). Coverage is uneven and that matters for how you use it: "
        "accommodation is nationwide, points of interest are regional (Zurich, "
        "Eastern Switzerland, Liechtenstein, Engadin Scuol), and events are "
        "nearly empty. Every hit carries its own provider, licence and copyright "
        "notice — quote them. Start with `search`; `get_details` takes an "
        "identifier from a hit. An empty result carries a `hint` — follow it "
        "before concluding that something does not exist."
    ),
    lifespan=app_lifespan,
)


# ---------------------------------------------------------------------------
# Tool plumbing
# ---------------------------------------------------------------------------

# Every tool reads a public tourism index and changes nothing. `openWorldHint`
# because the data comes from an external source the server does not control.
_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}


def _annotations(title: str) -> dict[str, object]:
    return {"title": title, **_READ_ONLY}


def _client(ctx: Context) -> DiscoverSwissClient:
    """The one shared client from the lifespan, or a named configuration error.

    The key is checked here and not left to the API: `/search` answers 401
    without one, and the client reads a 401 on `/search` as "entitlement
    withdrawn" — ten minutes of `search_unavailable` for a missing variable.
    """
    app: AppContext = ctx.request_context.lifespan_context
    if app.client is None or app.settings is None:
        raise ToolError("Server configuration is invalid; see the server log.")
    if not app.settings.api_key.get_secret_value():
        raise ToolError(
            "DISCOVER_SWISS_KEY is not set. This server is bring-your-own-key: create a "
            "subscription at portal.discover.swiss and export the key."
        )
    return app.client


def _fail(exc: Exception, tool: str, log) -> NoReturn:
    """Log the original error, raise a masked ``ToolError`` (OBS-001, OBS-002).

    States the model can act on — quota, unreachable, search refused — never
    get here: the tools return those as ``degraded`` envelopes. What arrives
    here is configuration or a bug, and the model gets one sentence saying
    which, not a stack trace.
    """
    if isinstance(exc, ToolError):
        raise exc
    log.exception("tool_execution_failed", tool=tool)
    if isinstance(exc, AuthorizationError):
        message = "discover.swiss refused the subscription key; check DISCOVER_SWISS_KEY."
    elif isinstance(exc, UpstreamRejectedError | NotFoundError):
        message = (
            "discover.swiss rejected the request as malformed. This is a server defect, "
            "not an empty result — do not conclude anything about the data."
        )
    elif isinstance(exc, net.EgressError):
        message = "The outbound request was blocked by the server's egress policy."
    else:
        message = "An unexpected internal error occurred; the details are in the server log."
    raise ToolError(f"{tool}: {message}") from exc


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(name="search", annotations=_annotations("Search Swiss tourism data"))
async def search(params: SearchInput, ctx: Context) -> SearchResponse:
    """Full-text and geo search over discover.swiss open tourism data (~20k objects: hotels nationwide; museums, restaurants, shops, tours, webcams, ski resorts for Zurich, Eastern Switzerland, Liechtenstein, Engadin). `query` is matched in name AND descriptions by default (`match='all'`), so a hit count includes objects that merely mention the term; use `match='name'` to match names only. Query syntax: plain words. The source documents no operators; wildcards (*, ?), quotes, AND/OR and prefixes are untested — send whole words, not fragments or operators. `near` ranks by distance from a coordinate; `locality` filters by the exact municipality name in the address. Rooms and meeting rooms are excluded unless requested via `types`. Every hit carries its own licence and attribution — cite the provider when you present it. Empty result: follow the `hint` before concluding anything.

    `types` takes leafType values (Hotel, Museum, Restaurant, HikingTrail, Webcam, Event, HotelRoom, MeetingRoom), ORed. `radius_km` only works together with `near` and is a hard cut-off; without it `near` only sorts. With a `query`, text relevance outweighs distance in that order — the nearest match is not necessarily first; use `radius_km` to bound the area and read `distance_km`, which is exact on every hit. `upstream_count` is the source's total before filtering; `returned` is what this page holds after the licence gate, the test-data filter and the room default — each exclusion is counted in its own `excluded_*` field. Page through with `page` while `has_more` is true. For full text, fees and accessibility of one hit, call `get_details` with its `identifier`.
    """
    log = tool_logger("search")
    client = _client(ctx)
    try:
        log.info("tool_call", query=params.query, types=params.types, page=params.page)
        return await search_impl(client, params)
    except Exception as exc:
        _fail(exc, "search", log)


@mcp.tool(name="get_details", annotations=_annotations("Details of one tourism object"))
async def get_details(params: GetDetailsInput, ctx: Context) -> DetailResponse:
    """Full details for one object by identifier: description, address, opening hours, fees, accessibility (Pro Infirmis profiles), amenities, star rating, check-in times, photos, links. Response is trimmed to ~8 KB. If `no_derivatives` is true the description is licensed CC BY-ND: quote it verbatim or summarise facts, do not rewrite it as your own text. Opening hours and prices are provider-maintained and can be outdated — say so when you present them (see `disclaimer`).

    `identifier` must come from a hit of `search`, `find_accommodation` or `find_tours`. `removed: true` means the provider withdrew the object; its data is shown but may be stale. An object whose licence is not open is returned as name, licence and attribution only, with `excluded_by_license: 1` — name it and link to the provider, do not describe it.
    """
    log = tool_logger("get_details")
    client = _client(ctx)
    try:
        log.info("tool_call", identifier=params.identifier)
        return await get_details_impl(client, params)
    except Exception as exc:
        _fail(exc, "get_details", log)


@mcp.tool(name="find_accommodation", annotations=_annotations("Find hotels and lodging"))
async def find_accommodation(params: FindAccommodationInput, ctx: Context) -> AccommodationResponse:
    """Find hotels and other lodging near a point or in a municipality. Covers 5'275 establishments nationwide (Zermatt to Geneva), not only the regions where points of interest exist. Star ratings are the official HotellerieSuisse classification (`stars`, `garni`, `superior`). `accessible=true` keeps lodgings with an accessibility profile from Pro Infirmis or OK:GO; each hit lists its accessibility data sources, and `get_details` returns the profiles themselves (wheelchair, stroller, hearing, vision). `price_range` is the provider's own band (Niedrig/Mittel/Hoch). This source has NO availability and NO nightly prices — never state that a room is free or what a night costs.

    Give `near` (ranks by distance, each hit carries `distance_km`; add `radius_km` for a hard cut-off) or `locality` (exact municipality name from the address). `amenities` are amenity feature names, ORed. Every hit carries its own licence and attribution — cite the provider. `disclaimer` applies to everything shown.
    """
    log = tool_logger("find_accommodation")
    client = _client(ctx)
    try:
        log.info("tool_call", locality=params.locality, accessible=params.accessible)
        return await find_accommodation_impl(client, params)
    except Exception as exc:
        _fail(exc, "find_accommodation", log)


@mcp.tool(name="find_tours", annotations=_annotations("Find hiking, cycling and winter tours"))
async def find_tours(params: FindToursInput, ctx: Context) -> ToursResponse:
    """Find hiking, cycling, mountain-bike, theme and winter tours (223 in total) in Eastern Switzerland (Glarnerland, St. Gallen, Thurgau, Appenzell, Toggenburg, Heidiland), the Zurich region, Liechtenstein and Engadin Scuol. The source has no tours for the Bernese Oberland, Valais, Ticino or Central Switzerland.

    Filters: `kind` (hiking, cycling, mtb, winter, theme, all), `difficulty_max` (1 easy – 3 hard), `length_km_max`, `ascent_m_max` (metres), `season_month` (1–12). `kind` follows the provider's classification: `hiking` also returns snowshoe routes filed as routes, and a theme trail can be a cycling rally. Every filter only matches tours that carry the value — a tour without length, ascent, difficulty or season data is not returned when that filter is set, and `season_month` in particular keeps a small minority of tours. Place: `region` (area name such as 'Glarnerland', resolved to an area id; `area` in the response shows what it resolved to and flags ambiguous names), `near` (+ optional `radius_km`) or `locality`. Each hit reports `length_km`, `ascent_m`, `descent_m`, `difficulty`, `duration_min` where the provider supplies them — RailAway products often lack length and ascent. `provider` names the source: SchweizMobil tours are CC BY, contentdesk tours CC BY-SA; cite it. Trail conditions and closures are not in this source.
    """
    log = tool_logger("find_tours")
    client = _client(ctx)
    try:
        log.info("tool_call", region=params.region, kind=params.kind)
        return await find_tours_impl(client, params)
    except Exception as exc:
        _fail(exc, "find_tours", log)


@mcp.tool(name="find_events", annotations=_annotations("Find events in a date range"))
async def find_events(params: FindEventsInput, ctx: Context) -> EventsResponse:
    """Find events whose schedule overlaps a date range (default: today to today + 30 days, Europe/Zurich). Event coverage in this source is thin (about 20 objects, mostly Eastern Switzerland; Zurich events are not included because their provider is not open-licensed).

    An event is included when any of its dates overlaps `from_date`–`to_date` (whole days). Place: `near` (+ optional `radius_km`), `locality` (exact municipality name from the address, e.g. 'St.Gallen' and 'St. Gallen' are different values) or `region` (area name, resolved to an area id; `area` shows the result). Each hit has `next_occurrence`, and `start`/`end` from the schedule entry that overlaps the range. `date_open: true` means the provider gives no concrete date — present it with `date_note` («Termin offen»), never with a guessed date. Test records and events that are not openly licensed are withheld and counted (`excluded_test_objects`, `excluded_by_license`). Dates and prices are provider-maintained — see `disclaimer`; cite the provider from `attribution`.
    """
    log = tool_logger("find_events")
    client = _client(ctx)
    try:
        log.info("tool_call", region=params.region, locality=params.locality)
        return await find_events_impl(client, params)
    except Exception as exc:
        _fail(exc, "find_events", log)


@mcp.tool(name="webcams_near", annotations=_annotations("Webcams near a place"))
async def webcams_near(params: WebcamsNearInput, ctx: Context) -> WebcamsResponse:
    """Webcams within a radius of a point (`near`, `radius_km`, default 25 km, nearest first) or in a region (`region`, area name resolved to an area id). 73 webcams, all in Eastern Switzerland (St. Gallen, Thurgau, Toggenburg, Heidiland, Glarnerland, Appenzell). `live_url` opens the provider's live image; `snapshot_url` is a stored still and may be hours old.

    Each hit carries `distance_km` when `near` is given; `upstream_count` is the number of webcams in the radius, 20 per `page`. Cite the provider from `attribution`. The webcam shows the view, not trail or road conditions.
    """
    log = tool_logger("webcams_near")
    client = _client(ctx)
    try:
        log.info("tool_call", region=params.region, radius_km=params.radius_km)
        return await webcams_near_impl(client, params)
    except Exception as exc:
        _fail(exc, "webcams_near", log)


@mcp.tool(name="explore_area", annotations=_annotations("What exists in an area"))
async def explore_area(params: ExploreAreaInput, ctx: Context) -> ExploreAreaResponse:
    """Overview of what exists in a region before searching: counts by object type, data owner, season, price range. Use it to decide which tool to call next and to avoid asking for things this source does not have. Counts are upstream counts before licence filtering.

    Scope: `region` (area name, resolved to an area id), `locality` (exact municipality name from the address) or `near` with `radius_km` (default 10); none of them means the whole index. `facets` takes OData names: leafType, containedInPlace/id, rating/difficulty, sourcePartner, season, priceRange, address/addressLocality, categoryTree (short forms containedInPlace, ratingDifficulty, addressLocality are mapped). Each facet lists up to 20 values as {value, label, count}; `containedInPlace/id` lists area ids with counts, and those area names are what `region` accepts elsewhere. Any other facet name is not sent (the upstream API rejects the whole request for it) and is reported in `missing_facets`, as is a sent facet that does not come back — a facet is never silently absent.
    """
    log = tool_logger("explore_area")
    client = _client(ctx)
    try:
        log.info("tool_call", region=params.region, facets=params.facets)
        return await explore_area_impl(client, params)
    except Exception as exc:
        _fail(exc, "explore_area", log)


@mcp.tool(name="source_status", annotations=_annotations("Health and scope of this server"))
async def source_status(ctx: Context) -> SourceStatusResponse:
    """Health and scope of this server. Call it first when another tool returned `degraded` or an unexpected empty result.

    Reports whether discover.swiss answers (`reachable`), whether its search endpoint is usable (`search_available`; if not, `search` and `find_accommodation` answer from typed lists), calls in the last minute against a limit of 60, since when the monthly quota is exhausted, the last successful call, the index size (`index_total`), the coverage of this source and the state of the written search entitlement. Works without a subscription key and then says so.
    """
    log = tool_logger("source_status")
    app: AppContext = ctx.request_context.lifespan_context
    if app.client is None:
        raise ToolError("Server configuration is invalid; see the server log.")
    try:
        log.info("tool_call")
        return await source_status_impl(app.client)
    except Exception as exc:
        _fail(exc, "source_status", log)


def main() -> None:
    """Start the server on the transport named by the environment."""
    try:
        settings = load_settings(require_key=False)
    except ConfigError as exc:
        configure_logging("INFO")
        logger.error("settings_invalid", error=str(exc))
        raise SystemExit(2) from exc
    # JSON logging to stderr; stdout belongs to the JSON-RPC stream.
    configure_logging(settings.log_level)

    if settings.transport == "streamable-http":
        import uvicorn

        from discover_swiss_mcp.http_app import build_http_app

        # Bind policy, port-exact Host/Origin lists and inbound OAuth are
        # decided in one place (http_app); an unsafe combination stops here.
        try:
            app, _verifier = build_http_app(mcp, settings)
        except ConfigError as exc:
            logger.error("http_start_refused", error=str(exc))
            raise SystemExit(2) from exc
        uvicorn.run(app, host=settings.host, port=settings.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
