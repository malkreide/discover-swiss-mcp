"""HTTP client for the discover.swiss Infocenter V2 API.

Everything the eight tools of P2/P3 share lives here: the outbound call with
its rate-limit budget and retry ladder, the in-memory cache, the search and
list endpoints, the detail fetch, the area lookup and the narrow fallback that
keeps the server usable if search entitlement is withdrawn.

**The probe is the source of truth, not the documentation.** The live probe of
2026-09-17 (``probes/PROBE_REPORT_discover-swiss-mcp.md``) contradicts the
published docs in three places that matter here, and this file follows the
probe every time:

* the docs say the Open product cannot use ``/search``; live it answers 200 as
  long as ``project`` travels in the body as an array,
* the paging token is ``nextPageToken`` (a string) next to ``hasNextPage`` (a
  bool), not the documented ``continuation``,
* the documented example project ``demo-web`` answers 400; ``dsod-content`` is
  the one that works.

Two behaviours in here exist because the index answers *quietly* rather than
with an error, and a quiet answer is the one that gets believed:

* an unknown facet name is ignored without a word, so every facet response is
  compared against the request and the difference is reported as
  ``missing_facets`` — never swallowed,
* ``top=1000`` is a wish, not a promise (Cosmos DB cuts at roughly 4 MB), so a
  caller that wants a complete set follows ``nextPageToken`` instead of
  trusting one page.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import time
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field

from discover_swiss_mcp import net
from discover_swiss_mcp._version import __version__
from discover_swiss_mcp.config import Settings
from discover_swiss_mcp.logging_config import get_logger

logger = get_logger("discover_swiss_mcp.client")

USER_AGENT = f"discover-swiss-mcp/{__version__} (+https://github.com/malkreide/discover-swiss-mcp)"

# ---------------------------------------------------------------------------
# Measured constants
# ---------------------------------------------------------------------------

# Search `select` whitelist: `IndexResponse` minus `containedInPlace` and
# `context` — 46 of 48 fields. Sending all 48 answers 400, and the two rejects
# were found by asking for each field on its own (probe run 3, PROBE_DETAIL
# section b). Hard-coded rather than derived: a list built from the live spec
# would start failing the moment the spec grows a 49th field.
#
# Note what is *not* in here: `license` and `copyrightNotice` are not fields of
# `IndexResponse` at all, so a search hit can never carry them. The licence of
# a search hit is derived from `dataGovernance` — see `licenses.license_of`.
SEARCH_SELECT_FIELDS: tuple[str, ...] = (
    "@id",
    "ouaId",
    "identifier",
    "datasource",
    "dataGovernance",
    "type",
    "additionalType",
    "additionalProperty",
    "address",
    "geo",
    "geoDestination",
    "openingHours",
    "image",
    "name",
    "disambiguatingDescription",
    "description",
    "state",
    "time",
    "length",
    "rating",
    "tag",
    "campaignTag",
    "profileTag",
    "schedule",
    "openingHoursSpecification",
    "specialOpeningHoursSpecification",
    "nextOccurrence",
    "recurredCount",
    "elevation",
    "link",
    "autoTranslatedData",
    "ticketingContact",
    "priceInformation",
    "standardPrice",
    "potentialAction",
    "organizer",
    "lastModified",
    "sourceId",
    "hasReview",
    "location",
    "category",
    "productAvailability",
    "starRating",
    "award",
    "relevanceScore",
    "awardSimplex",
)
SEARCH_SELECT = ",".join(SEARCH_SELECT_FIELDS)

# List-endpoint `select`. Fifteen fields, every one of them answered live rather
# than assumed: the first nine come from the probe of 2026-09-17, the last six
# from `probes/probe_open.py` on 2026-09-23, which asked for them on
# `/lodgingbusinesses`, `/civicStructures` and `/webcams` — three different
# response definitions — and got 200 from all three.
#
# The endpoint-by-endpoint check is not ceremony. Each list endpoint has its own
# response definition, so a field that is fine on `/lodgingbusinesses` can 400 on
# `/webcams`, and a 400 here fails the whole page rather than dropping the field.
# Adding a sixteenth is the same live check again, not a guess.
#
# `select` is never omitted: without it a row costs ~9.5 KB instead of ~1 KB.
LIST_SELECT_FIELDS: tuple[str, ...] = (
    "identifier",
    "name",
    "type",
    "additionalType",
    "license",
    "copyrightNotice",
    "dataGovernance",
    "geo",
    "containedInPlace",
    # Measured 2026-09-23. These are what make the fallback answer a real
    # question: without `address` and `url` a hit is a name and a coordinate.
    "address",
    "url",
    "link",
    "image",
    "lastModified",
    "telephone",
)
LIST_SELECT = ",".join(LIST_SELECT_FIELDS)

# The content collections of the Open product, from the probe's endpoint matrix.
# A frozenset rather than free-form input: the endpoint goes into a URL path,
# and a path segment a caller controls is how a client ends up fetching
# something nobody designed it to fetch.
LIST_ENDPOINTS: frozenset[str] = frozenset(
    {
        "accommodations",
        "areas",
        "civicStructures",
        "events",
        "foodEstablishments",
        "imageObjects",
        "localbusinesses",
        "lodgingbusinesses",
        "places",
        "products",
        "skiresorts",
        "tours",
        "transportationSystems",
        "webcams",
    }
)

# Facet names the index answers under, verified live (PROBE_VERIFY section 1,
# 2026-09-17): all eight came back under exactly these keys.
VERIFIED_FACETS: tuple[str, ...] = (
    "leafType",
    "containedInPlace/id",
    "rating/difficulty",
    "sourcePartner",
    "season",
    "priceRange",
    "address/addressLocality",
    "categoryTree",
)

# The `filterPropertyName` spellings of the same facets. The spec says they are
# equivalent («rating/condition and ratingCondition returns same facet»); live,
# `containedInPlace` and `ratingDifficulty` produced no facet and no error. So
# they are rewritten before they leave, rather than sent to be dropped.
FACET_ALIASES: dict[str, str] = {
    "containedInPlace": "containedInPlace/id",
    "ratingDifficulty": "rating/difficulty",
    "addressLocality": "address/addressLocality",
}


def odata_facet_names(names: list[str]) -> list[str]:
    """Map short facet names to their OData names; keep everything else as given."""
    mapped: list[str] = []
    for name in names:
        candidate = FACET_ALIASES.get(name.strip(), name.strip())
        if candidate and candidate not in mapped:
            mapped.append(candidate)
    return mapped


def partition_facet_names(names: list[str]) -> tuple[list[str], list[str]]:
    """``(sendable, unknown)``: verified OData names, and everything else.

    Only verified names leave the client. An unknown name is not dropped
    quietly upstream, as the probe suggested — the live stop-gate run of
    2026-09-26 answered ``facets=[leafType, difficultyX]`` with HTTP 400 for
    the whole request. The quiet drop only applies to the ``filterPropertyName``
    spellings of real facets, which :data:`FACET_ALIASES` rewrites first.
    """
    sendable: list[str] = []
    unknown: list[str] = []
    for name in odata_facet_names(names):
        (sendable if name in VERIFIED_FACETS else unknown).append(name)
    return sendable, unknown


# Identifiers look like `civ_px9-s28_bggg` or
# `tou_s9t_acfeirar-ficg-ejes-qatg-crjfhetqhvev`. The pattern is a gate, not a
# parser: it keeps `../` and a stray `%2f` out of the URL path.
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

# Published quota: 60 calls per minute, 50'000 per month. The client-side bucket
# sits at 55 so that a burst hits our own brake before the gateway's — a 429 is
# a wait either way, but one we cause ourselves is one we can shape.
RATE_LIMIT_PER_MINUTE = 55
RATE_LIMIT_WINDOW_SECONDS = 60.0

REQUEST_TIMEOUT = 20.0

# Retry ladder for 5xx and network errors: three retries after the first
# attempt, waiting 2 s, 4 s, 8 s. Deliberately without jitter — this is a
# single-process, bring-your-own-key client whose admissions are already
# serialised by the token bucket above, so there is no fleet to de-synchronise,
# and a fixed ladder is one a test can assert on exactly.
RETRY_DELAYS: tuple[float, ...] = (2.0, 4.0, 8.0)

# A cap on the whole call — every attempt and every wait together. A number of
# attempts is not a limit: four attempts against an upstream that needs the full
# timeout is over a minute inside one tool call, and `RETRY_DELAYS` says that
# nowhere. The anchor is the MCP SDK's own 30 s default client timeout; past it
# nobody is listening any more, while the load still lands on the source.
TOTAL_BUDGET = 25.0

# Every wait counts against `TOTAL_BUDGET` — the retry ladder, a 429's named
# wait («Try again in N seconds») and the client-side token bucket alike. The
# first version let a 429 extend the budget by up to 30 s, which put one tool
# call at about 55 s — past the MCP client's own 30 s, so the answer arrived
# for nobody (audit ARCH-014). A wait that no longer fits ends the call at once
# as `RateLimitedError`, carrying the seconds, so the tool can say «try again
# in N seconds» instead of hanging and then failing.

# Cache TTLs. Search results move slowly (the index is rebuilt, not edited
# live), detail objects even more slowly, and facet distributions are a shape
# rather than a fact. All three exist to keep the monthly 50'000 from being
# spent on repeated identical questions in one conversation.
SEARCH_TTL_SECONDS = 15 * 60
FACET_TTL_SECONDS = 60 * 60
VERTEX_TTL_SECONDS = 24 * 60 * 60

# How long a refused `/search` keeps the fallback path on. Short enough that a
# transient refusal heals by itself, long enough not to re-probe on every call.
SEARCH_UNAVAILABLE_SECONDS = 10 * 60

CACHE_MAX_ENTRIES = 512

Provenance = Literal["live_api", "cached", "list_fallback"]

# Indirections so tests can control time without patching the stdlib. Patching
# `asyncio.sleep` or `time.monotonic` looks local and is not: it changes every
# caller in the process — the event loop reads `time.monotonic` too — and a
# test then measures its own patch (audit OPS-010). `tests/test_client.py`
# guards both seams.
_sleep = asyncio.sleep
_monotonic = time.monotonic


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class DiscoverSwissError(RuntimeError):
    """Base class. ``degraded`` is the value the tool puts in the envelope."""

    degraded: str | None = None


class UpstreamUnavailableError(DiscoverSwissError):
    """Network failure, timeout, or 5xx that survived the retry ladder."""

    degraded = "upstream_unreachable"


class RateLimitedError(DiscoverSwissError):
    """A wait — the upstream's 429 or our own bucket — does not fit the budget."""

    degraded = "rate_limited"

    def __init__(self, message: str, retry_after: float) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class UpstreamShapeError(DiscoverSwissError):
    """The answer does not have the structure the reader relies on (audit FID-006).

    Raised instead of reading an empty list out of a shape we do not
    recognise: a moved root key would otherwise arrive as «no hit» — the one
    outcome a model cannot tell from a real empty result.
    """

    degraded = "upstream_shape_changed"


class QuotaExhaustedError(DiscoverSwissError):
    """403 carrying «quota»: the monthly contingent is spent.

    Not a transient failure and never retried — a retry cannot create quota,
    it only spends the little that a reset might bring back.
    """

    degraded = "quota_exhausted"


class SearchUnavailableError(DiscoverSwissError):
    """``/search`` refused the key. The documented state, live since never."""

    degraded = "search_unavailable"


class AuthorizationError(DiscoverSwissError):
    """401/403 outside ``/search`` — a configuration problem, not a data one."""


class UpstreamRejectedError(DiscoverSwissError):
    """A 4xx that says the request was wrong. Retrying sends the same request."""


class InvalidIdentifierError(UpstreamRejectedError):
    """The identifier failed the shape gate; nothing was sent upstream.

    The one rejection `get_details` may report as «unknown identifier»: it is
    the server's own verdict about the input. A 4xx *from discover.swiss* is
    not — it says the request was wrong, not that the object is absent
    (audit FID-003).
    """


class NotFoundError(DiscoverSwissError):
    """404 on a path that should have carried an object."""


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


class SearchResult(BaseModel):
    """One ``POST /search`` answer, unwrapped but not reshaped."""

    count: int | None
    values: list[dict[str, Any]] = Field(default_factory=list)
    facets: dict[str, Any] = Field(default_factory=dict)
    # Facet names that were asked for and did not come back. The index drops
    # unknown names without a word; this is that silence, made visible.
    missing_facets: list[str] = Field(default_factory=list)
    provenance: Provenance = "live_api"
    retrieved_at: datetime


class ListPage(BaseModel):
    """One page of a list endpoint."""

    data: list[dict[str, Any]] = Field(default_factory=list)
    next_token: str | None = None
    has_next_page: bool = False
    total: int | None = None
    provenance: Provenance = "live_api"
    retrieved_at: datetime


class AreaSuggestion(BaseModel):
    identifier: str
    name: str
    count: int | None = None


class AreaLookup(BaseModel):
    """The result of resolving an area name to an area id.

    ``suggestions`` carries the alternatives in both directions: the closest
    areas when nothing matched, and the rival areas of the same name when
    something did and ``ambiguous`` is set.
    """

    query: str
    identifier: str | None = None
    name: str | None = None
    # True when more than one area carries exactly this name. The id is still
    # filled — with the largest — but the caller has to say so.
    ambiguous: bool = False
    suggestions: list[AreaSuggestion] = Field(default_factory=list)
    hint: str | None = None
    provenance: Provenance = "live_api"
    retrieved_at: datetime


# ---------------------------------------------------------------------------
# Rate limiting and caching
# ---------------------------------------------------------------------------


class TokenBucket:
    """A sliding-window admission gate over the last minute."""

    def __init__(
        self,
        limit: int = RATE_LIMIT_PER_MINUTE,
        window: float = RATE_LIMIT_WINDOW_SECONDS,
    ) -> None:
        self._limit = limit
        self._window = window
        self._stamps: list[float] = []
        self._lock = asyncio.Lock()

    def _prune(self, now: float) -> None:
        cutoff = now - self._window
        self._stamps = [t for t in self._stamps if t > cutoff]

    @property
    def calls_last_minute(self) -> int:
        self._prune(_monotonic())
        return len(self._stamps)

    async def acquire(self, max_wait: float | None = None) -> None:
        """Wait, if needed, until a call fits inside the window.

        ``max_wait`` is what is left of the caller's budget. A wait longer than
        that is not taken: it raises :class:`RateLimitedError` at once.
        """
        async with self._lock:
            now = _monotonic()
            self._prune(now)
            if len(self._stamps) >= self._limit:
                wait = self._window - (now - self._stamps[0]) + 0.05
                if max_wait is not None and wait > max_wait:
                    raise RateLimitedError(
                        f"Client-side rate limit ({self._limit} calls/minute): the next call "
                        f"is possible in {wait:.0f} s.",
                        retry_after=wait,
                    )
                if wait > 0:
                    logger.info("rate_limit_wait", seconds=round(wait, 2))
                    await _sleep(wait)
                self._prune(_monotonic())
            self._stamps.append(_monotonic())


class TTLCache:
    """A small in-memory cache with per-entry TTL and a bounded size."""

    def __init__(self, max_entries: int = CACHE_MAX_ENTRIES) -> None:
        self._entries: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._max_entries = max_entries

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at <= _monotonic():
            del self._entries[key]
            return None
        self._entries.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        now = _monotonic()
        self._entries[key] = (now + ttl, value)
        self._entries.move_to_end(key)
        # Expired first, oldest after — dropping a live entry while a dead one
        # holds a slot is the kind of cache that costs calls instead of saving
        # them.
        for key_ in [k for k, (exp, _) in self._entries.items() if exp <= now]:
            del self._entries[key_]
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)

    def clear(self) -> None:
        self._entries.clear()

    def live_entries(self) -> int:
        """Entries that have not expired — what ``source_status`` reports."""
        now = _monotonic()
        return sum(1 for expires_at, _ in self._entries.values() if expires_at > now)

    def __len__(self) -> int:  # pragma: no cover - diagnostics
        return len(self._entries)


def _cache_key(kind: str, lang: str, payload: Any) -> str:
    return f"{kind}|{lang}|{json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)}"


# ---------------------------------------------------------------------------
# Helpers the tools share
# ---------------------------------------------------------------------------


def _as_suggestion(value: dict[str, Any]) -> AreaSuggestion:
    """One facet value as an area suggestion."""
    return AreaSuggestion(
        identifier=str(value.get("value")),
        name=str(value.get("name")),
        count=value.get("count") if isinstance(value.get("count"), int) else None,
    )


# Values per facet in an area lookup. The facet is ordered by content volume,
# so these are the 30 areas holding the most matches for the name.
AREA_FACET_VALUES = 30


def facet_request(name: str, count: int) -> dict[str, Any]:
    """One FacetRequest, with the ordering the readers rely on sent explicitly.

    `resolve_area` takes the largest areas and suggests the first three;
    `explore_area` reports «the top N». Both depend on count-descending order,
    which is the documented default — and a default this code relies on is
    sent, not inherited (audit FID-001; see docs/DEFAULTS.md).
    """
    return {"name": name, "count": count, "orderBy": "count", "orderDirection": "desc"}


def facet_values(facets: dict[str, Any], name: str) -> list[dict[str, Any]]:
    """The value list of one facet, or ``[]`` if it is not in the answer."""
    facet = facets.get(name)
    if isinstance(facet, dict):
        values = facet.get("values")
        if isinstance(values, list):
            return [v for v in values if isinstance(v, dict)]
    return []


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres (haversine, mean Earth radius)."""
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def filter_by_distance(
    rows: list[dict[str, Any]], lat: float, lon: float, radius_km: float
) -> list[dict[str, Any]]:
    """Keep the rows within ``radius_km`` of a point, nearest first.

    Only for the fallback path. ``/search`` has a real radius filter
    (``geo.distance(geo, geography'POINT(lon lat)') le <km>``), and clipping
    client-side there would throw away matches the index already counted.
    A row without usable coordinates is dropped, not kept on the benefit of the
    doubt: a hit whose distance is unknown cannot answer «how far is it».
    """
    scored: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        geo = row.get("geo")
        if not isinstance(geo, dict):
            continue
        try:
            row_lat = float(geo["latitude"])
            row_lon = float(geo["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        distance = distance_km(lat, lon, row_lat, row_lon)
        if distance <= radius_km:
            scored.append((distance, row))
    scored.sort(key=lambda pair: pair[0])
    return [row for _, row in scored]


def _confirm_envelope(payload: Any, path: str, rows_key: str) -> tuple[int | None, list[Any]]:
    """The count and the rows of a response — or :class:`UpstreamShapeError`.

    Checks only what the reader touches: the root is an object, the rows key
    holds a list, and a positive count comes with rows to read. A zero count
    with the rows key missing or null stays a legitimate empty result; the
    recorded responses never show which of the two the source sends for zero,
    so both are accepted. What is refused is the silent case this exists for:
    the source says 53, the reader finds nothing, and «no hit» goes out.
    """
    if not isinstance(payload, dict):
        raise UpstreamShapeError(f"{path} answered {type(payload).__name__}, not an object.")
    raw_count = payload.get("count")
    count = raw_count if isinstance(raw_count, int) and not isinstance(raw_count, bool) else None
    rows = payload.get(rows_key)
    if rows is None:
        if rows_key not in payload and "count" not in payload:
            raise UpstreamShapeError(
                f"{path} answered without `{rows_key}` and without `count`; "
                f"keys were {sorted(payload)[:8]}."
            )
        if count:
            raise UpstreamShapeError(
                f"{path} reports {count} results but carries no `{rows_key}` list."
            )
        return count, []
    if not isinstance(rows, list):
        raise UpstreamShapeError(
            f"{path} answered `{rows_key}` as {type(rows).__name__}, not a list."
        )
    return count, rows


def _retry_after_seconds(payload: Any, headers: httpx.Headers | None) -> float:
    """Seconds to wait after a 429, read from the body, then the header.

    The gateway writes «Rate limit is exceeded. Try again in 33 seconds.» into
    the body; the header is the fallback, and 60 s — one full window — the
    fallback of last resort.
    """
    body = json.dumps(payload, ensure_ascii=False, default=str) if payload is not None else ""
    match = re.search(r"try again in\s+(\d+)\s*second", body, re.IGNORECASE)
    if not match:
        match = re.search(r"(\d+)\s*seconds", body, re.IGNORECASE)
    if match:
        # One second on top: the named value is where the window ends, and
        # arriving exactly on the boundary earns a second 429.
        return float(match.group(1)) + 1.0
    raw = (headers or httpx.Headers()).get("retry-after", "").strip()
    if raw.isdigit():
        return float(raw) + 1.0
    return RATE_LIMIT_WINDOW_SECONDS


def _total_from(payload: Any) -> int | None:
    """The total from ``includeCount=true``.

    The list responses call it ``count`` — the spec says so and
    `probes/probe_open.py` confirmed it on the live envelopes of
    `/tours`, `/civicStructures`, `/lodgingbusinesses` and `/webcams`. The
    tolerant second pass stays anyway: reading a number out of the answer that
    arrives is cheaper than being wrong about it after a release note nobody
    saw.
    """
    if not isinstance(payload, dict):
        return None
    value = payload.get("count")
    if isinstance(value, int):
        return value
    for key, candidate in payload.items():
        if isinstance(candidate, int) and not isinstance(candidate, bool):
            if re.search(r"count|total", key, re.IGNORECASE):
                return candidate
    return None


def _next_token_from(payload: Any) -> str | None:
    """The paging token — the **string**, never the ``hasNextPage`` bool.

    Sending the boolean as a token answers 400. It is in the probe's findings
    list because it is the mistake the documentation invites.
    """
    if not isinstance(payload, dict):
        return None
    for key in ("nextPageToken", "continuationToken", "continuation"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class DiscoverSwissClient:
    """Async wrapper around the Infocenter V2 endpoints.

    One shared client per server process, created in the server lifespan and
    closed on shutdown — not one per tool call.
    """

    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._http = http_client
        self._owns_http = http_client is None
        self._bucket = TokenBucket()
        self._cache = TTLCache()
        self._quota_exhausted_since: datetime | None = None
        self._last_success: datetime | None = None
        self._search_unavailable_until: float | None = None

    # -- plumbing ----------------------------------------------------------

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def cache(self) -> TTLCache:
        return self._cache

    @property
    def calls_last_minute(self) -> int:
        return self._bucket.calls_last_minute

    @property
    def last_success(self) -> datetime | None:
        return self._last_success

    @property
    def search_available(self) -> bool:
        """Whether ``/search`` is believed to work right now."""
        if self._search_unavailable_until is None:
            return True
        if _monotonic() >= self._search_unavailable_until:
            self._search_unavailable_until = None
            return True
        return False

    def _client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            # follow_redirects=False: redirects are followed by `net.safe_request`
            # so every hop runs the SSRF and allow-list chain again.
            self._http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=False)
            self._owns_http = True
        return self._http

    def request_headers(self, lang: str = "de") -> dict[str, str]:
        """Headers for one outbound request.

        ``Accept-Language`` is always explicit — the API defaults to de-CH and
        silently returns German names otherwise — and ``categoryVersion: sui``
        follows the vendor's August 2025 warning even though the probe measured
        no visible effect on the list endpoints.
        """
        return {
            **self._settings.auth_header,
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": lang,
            "categoryVersion": "sui",
        }

    async def aclose(self) -> None:
        """Close the shared transport, if this client opened it."""
        if self._http is not None and self._owns_http and not self._http.is_closed:
            await self._http.aclose()
        self._http = None

    # -- the one outbound call --------------------------------------------

    async def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        lang: str = "de",
        allow_404: bool = False,
        search_endpoint: bool = False,
    ) -> Any:
        """Perform one API call with the rate budget, retries and error mapping.

        Returns the parsed payload (``None`` for 204 and, with ``allow_404``,
        for 404). Everything else raises a :class:`DiscoverSwissError`.
        """
        if self._quota_exhausted_since is not None:
            raise QuotaExhaustedError(
                "The monthly discover.swiss quota is exhausted "
                f"(first seen {self._quota_exhausted_since.isoformat()})."
            )

        url = f"{self._settings.base_url}{path}"
        params = {k: v for k, v in (params or {}).items() if v is not None}
        client = self._client()
        headers = self.request_headers(lang)

        deadline = _monotonic() + TOTAL_BUDGET
        retry_index = 0
        rate_limit_retries = 0

        while True:
            remaining = deadline - _monotonic()
            if remaining <= 0:
                raise UpstreamUnavailableError(
                    f"discover.swiss did not answer within {TOTAL_BUDGET:.0f} s."
                )

            await self._bucket.acquire(max_wait=remaining)
            try:
                async with asyncio.timeout(remaining):
                    response, _final_url = await net.safe_request(
                        client,
                        method,
                        url,
                        headers=headers,
                        params=params or None,
                        json_body=json_body,
                    )
            except TimeoutError as exc:
                raise UpstreamUnavailableError(
                    f"discover.swiss did not answer within {TOTAL_BUDGET:.0f} s."
                ) from exc
            except net.EgressError:
                raise
            except httpx.RequestError as exc:
                # `RequestError` is the superclass: a connection reset that is
                # neither a timeout nor a connect error is the same case and
                # would otherwise fall through uncovered.
                if retry_index >= len(RETRY_DELAYS):
                    raise UpstreamUnavailableError(
                        f"discover.swiss is not reachable ({type(exc).__name__})."
                    ) from exc
                delay = RETRY_DELAYS[retry_index]
                retry_index += 1
                if delay >= deadline - _monotonic():
                    raise UpstreamUnavailableError(
                        f"discover.swiss is not reachable ({type(exc).__name__})."
                    ) from exc
                logger.warning("upstream_retry", path=path, reason=type(exc).__name__, delay=delay)
                await _sleep(delay)
                continue

            status = response.status_code
            payload = _parse_json(response)

            if status in (200, 201, 204):
                self._last_success = datetime.now(UTC)
                return payload

            if status == 404:
                if allow_404:
                    self._last_success = datetime.now(UTC)
                    return None
                raise NotFoundError(f"discover.swiss has no object at {path}.")

            if status == 429:
                wait = _retry_after_seconds(payload, response.headers)
                # The named wait counts against the budget (see TOTAL_BUDGET);
                # one that does not fit, or a second 429, ends the call.
                if rate_limit_retries >= 1 or wait >= deadline - _monotonic():
                    raise RateLimitedError(
                        f"discover.swiss rate limit reached; it asks to wait {wait:.0f} s.",
                        retry_after=wait,
                    )
                rate_limit_retries += 1
                logger.warning("rate_limited", path=path, seconds=wait)
                await _sleep(wait)
                continue

            if status == 403 and "quota" in json.dumps(payload, default=str).lower():
                self._quota_exhausted_since = datetime.now(UTC)
                logger.error("quota_exhausted", path=path)
                raise QuotaExhaustedError(
                    "The monthly discover.swiss quota is exhausted; no retry will change that."
                )

            if status in (401, 403):
                if search_endpoint:
                    self._search_unavailable_until = _monotonic() + SEARCH_UNAVAILABLE_SECONDS
                    logger.error("search_unavailable", status=status)
                    raise SearchUnavailableError(
                        f"discover.swiss refused /search with HTTP {status}."
                    )
                raise AuthorizationError(
                    f"discover.swiss refused {path} with HTTP {status}; check DISCOVER_SWISS_KEY."
                )

            if status >= 500:
                if retry_index >= len(RETRY_DELAYS):
                    raise UpstreamUnavailableError(f"discover.swiss answered HTTP {status}.")
                delay = RETRY_DELAYS[retry_index]
                retry_index += 1
                if delay >= deadline - _monotonic():
                    raise UpstreamUnavailableError(f"discover.swiss answered HTTP {status}.")
                logger.warning("upstream_retry", path=path, status=status, delay=delay)
                await _sleep(delay)
                continue

            # Every other 4xx says the request was wrong. The third attempt
            # sends the same request and gets the same answer.
            raise UpstreamRejectedError(f"discover.swiss answered HTTP {status} for {path}.")

    # -- search ------------------------------------------------------------

    async def search(self, body: dict[str, Any], lang: str = "de") -> SearchResult:
        """``POST /search``.

        ``project`` is added here and always as an array — without it the
        endpoint answers 401, and that is the one parameter no caller may
        forget. ``select`` defaults to the verified 46-field whitelist.

        The cache is read before the availability check: an answer fetched
        while search still worked is as valid as it was a minute ago, and it
        is what lets an area lookup survive the switch to the list fallback.
        """
        request: dict[str, Any] = {
            "project": [self._settings.project],
            "select": SEARCH_SELECT,
            **{k: v for k, v in body.items() if v is not None},
        }
        # Restored after the caller's body, not before it: `project` is the one
        # parameter a tool must not be able to override by accident, and
        # `/search` answers 401 the moment it is wrong or missing.
        request["project"] = [self._settings.project]

        requested_facets = _requested_facet_names(request.get("facets"))
        ttl = FACET_TTL_SECONDS if requested_facets else SEARCH_TTL_SECONDS
        key = _cache_key("search", lang, request)

        cached = self._cache.get(key)
        if cached is not None:
            return cached.model_copy(update={"provenance": "cached"})

        if not self.search_available:
            raise SearchUnavailableError(
                "discover.swiss refused /search recently; the list fallback is the way in."
            )

        payload = await self._call(
            "POST", "/search", json_body=request, lang=lang, search_endpoint=True
        )
        count, values = _confirm_envelope(payload, "/search", rows_key="values")
        facets = payload.get("facets")
        if facets is not None and not isinstance(facets, dict):
            raise UpstreamShapeError(
                f"/search answered `facets` as {type(facets).__name__}, not an object."
            )
        facets = facets or {}
        missing = [name for name in requested_facets if name not in facets]
        if missing:
            # An unknown facet name is dropped without an error. Logging it is
            # half the job; the other half is `missing_facets` reaching the
            # envelope, so the model is told what it is not seeing.
            logger.warning("facets_missing", requested=requested_facets, missing=missing)

        result = SearchResult(
            count=count,
            values=[v for v in values if isinstance(v, dict)],
            facets=facets,
            missing_facets=missing,
            provenance="live_api",
            retrieved_at=datetime.now(UTC),
        )
        self._cache.set(key, result, ttl)
        return result

    # -- detail ------------------------------------------------------------

    async def get_vertex(self, identifier: str, lang: str = "de") -> dict[str, Any] | None:
        """``GET /vertices/{id}``. ``None`` only for 404.

        An object flagged ``removed: true`` is returned as it is. It is an
        answer — "this existed and is gone" — and turning it into ``None`` would
        make a withdrawn museum indistinguishable from a typo in the id.
        """
        if not _IDENTIFIER_PATTERN.match(identifier or ""):
            raise InvalidIdentifierError(f"{identifier!r} is not a discover.swiss identifier.")

        key = _cache_key("vertex", lang, identifier)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        payload = await self._call(
            "GET",
            f"/vertices/{quote(identifier, safe='')}",
            # includeAllPhotos: the documented default (false) skips
            # low-confidence images; sent so it is not inherited (FID-001).
            params={"project": self._settings.project, "includeAllPhotos": "false"},
            lang=lang,
            allow_404=True,
        )
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise UpstreamShapeError(
                f"/vertices answered {type(payload).__name__}, not a detail object."
            )
        self._cache.set(key, payload, VERTEX_TTL_SECONDS)
        return payload

    def is_vertex_cached(self, identifier: str, lang: str = "de") -> bool:
        """Whether :meth:`get_vertex` would answer this from the cache.

        Asked *before* the fetch, so ``get_details`` can report ``provenance:
        cached`` truthfully instead of labelling a day-old object as live.
        """
        return self._cache.get(_cache_key("vertex", lang, identifier)) is not None

    # -- list endpoints ----------------------------------------------------

    async def list_endpoint(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        lang: str = "de",
    ) -> ListPage:
        """One page of a list endpoint.

        ``project``, ``top`` and ``select`` always travel explicitly: omitting
        ``top`` silently means 10 rows, omitting ``project`` lands on an
        undocumented partner default, and omitting ``select`` multiplies the
        payload by nine.
        """
        name = endpoint.strip("/")
        if name not in LIST_ENDPOINTS:
            raise UpstreamRejectedError(
                f"{endpoint!r} is not a discover.swiss content collection ({sorted(LIST_ENDPOINTS)})."
            )

        merged: dict[str, Any] = {
            "project": self._settings.project,
            "top": 200,
            "select": LIST_SELECT,
            **{k: v for k, v in (params or {}).items() if v is not None},
        }
        # Same reason as in `search()`: the project is the server's, not the
        # caller's.
        merged["project"] = self._settings.project
        # Counting on every page pays for the same number again and again;
        # the first page is where it is worth a call.
        if "includeCount" not in merged:
            merged["includeCount"] = "false" if merged.get("continuationToken") else "true"

        payload = await self._call("GET", f"/{name}", params=merged, lang=lang)
        _count, rows = _confirm_envelope(payload, f"/{name}", rows_key="data")
        return ListPage(
            data=[r for r in rows if isinstance(r, dict)],
            next_token=_next_token_from(payload),
            has_next_page=bool(payload.get("hasNextPage")),
            total=_total_from(payload),
            provenance="live_api",
            retrieved_at=datetime.now(UTC),
        )

    async def list_fallback(
        self,
        type_endpoint: str,
        contained_in_place: str | None = None,
        top: int = 200,
        token: str | None = None,
        lang: str = "de",
    ) -> ListPage:
        """The narrow way in when ``/search`` is refused.

        Deliberately narrow, and deliberately not to be widened: no full text,
        no ranking, one collection at a time, optionally one area. Tools filter
        by distance client-side with :func:`filter_by_distance` and say so in
        the envelope — ``provenance: list_fallback``, ``degraded:
        search_unavailable``.

        The area filter is measured, not assumed. `probes/probe_open.py`, run
        2026-09-23: `/tours` 223 → 117 for `ds_glarnerland` and
        `/civicStructures` 1'406 → 232 for Zurich, both matching the search
        side exactly, and an invented area id returning 0 rather than the whole
        collection. That last number is the one that matters here — an id this
        client cannot resolve yields an empty page, not a silent full one, so a
        caller must read an empty result as "unknown area", never as "nothing
        there".
        """
        page = await self.list_endpoint(
            type_endpoint,
            {
                "top": top,
                "containedInPlace": contained_in_place,
                "continuationToken": token,
            },
            lang=lang,
        )
        logger.info(
            "list_fallback",
            endpoint=type_endpoint,
            contained_in_place=contained_in_place,
            rows=len(page.data),
        )
        return page.model_copy(update={"provenance": "list_fallback"})

    # -- areas -------------------------------------------------------------

    async def resolve_area(self, name: str, lang: str = "de") -> AreaLookup:
        """Resolve an area name to an area id via the ``containedInPlace/id`` facet.

        Not by paging ``/areas``: that is 7'290 rows for one lookup. The facet
        answers in a single call and ranks by how much content actually sits in
        the area — «Glarnerland» → ``ds_glarnerland`` (345 objects), verified
        live.

        Without an exact, case-insensitive name match this returns the three
        largest facet values as suggestions and no id. Picking the top hit
        would turn «Glarnerland» into «Schweiz», which is a different answer to
        a different question.

        An exact match is not automatically a unique one. The live run of
        2026-09-23 resolved «Zürich» to two areas bearing that exact name —
        ``osm_1690227`` with 894 objects and ``kire_zurich`` with 785 — and the
        first-hit rule would have chosen between them silently, which is the
        move this server exists not to make. The largest still wins, because a
        caller needs an id to work with, but ``ambiguous`` is set, the rival
        carries in ``suggestions``, and the ``hint`` names it.
        """
        result = await self.search(
            {
                "searchText": name,
                "resultsPerPage": 1,
                "select": "identifier",
                "facets": [facet_request("containedInPlace/id", AREA_FACET_VALUES)],
            },
            lang=lang,
        )
        if "containedInPlace/id" in result.missing_facets:
            # The area index did not come back. «No area is named X» would be a
            # statement about the data the server never saw (audit FID-L02).
            raise UpstreamShapeError(
                "/search did not return the containedInPlace/id facet; area names cannot "
                "be resolved until it does."
            )
        values = facet_values(result.facets, "containedInPlace/id")
        wanted = name.strip().casefold()

        exact = [
            value
            for value in values
            if str(value.get("name", "")).strip().casefold() == wanted and value.get("value")
        ]
        if exact:
            # Largest first: among areas of the same name, the one carrying more
            # content is the one a guest question almost always means.
            exact.sort(
                key=lambda v: v.get("count") if isinstance(v.get("count"), int) else -1,
                reverse=True,
            )
            chosen, rivals = exact[0], exact[1:]
            hint = None
            if rivals:
                logger.warning(
                    "area_name_ambiguous",
                    query=name,
                    chosen=chosen.get("value"),
                    rivals=[v.get("value") for v in rivals],
                )
                hint = (
                    f"{len(exact)} areas are named «{name}». Using "
                    f"«{chosen.get('name')}» ({chosen.get('value')}, "
                    f"{chosen.get('count')} objects) because it holds the most; the others are "
                    + ", ".join(f"{v.get('value')} ({v.get('count')})" for v in rivals)
                    + "."
                )
            return AreaLookup(
                query=name,
                identifier=str(chosen.get("value")),
                name=str(chosen.get("name")),
                ambiguous=bool(rivals),
                suggestions=[_as_suggestion(v) for v in rivals],
                hint=hint,
                provenance=result.provenance,
                retrieved_at=result.retrieved_at,
            )

        suggestions = [
            _as_suggestion(value)
            for value in values[:3]
            if value.get("value") and value.get("name")
        ]
        hint = f"No area is named exactly «{name}». " + (
            "Closest by content volume: "
            + ", ".join(f"«{s.name}» ({s.identifier})" for s in suggestions)
            + "."
            if suggestions
            else "The search text matched no area at all."
        )
        if len(values) >= AREA_FACET_VALUES:
            # The comparison ran over a truncated list; say so, or the hint
            # claims more than was checked.
            hint += (
                f" Only the {AREA_FACET_VALUES} areas holding the most matches were compared; "
                "a smaller area of that exact name may exist — try `near` with a coordinate."
            )
        return AreaLookup(
            query=name,
            suggestions=suggestions,
            hint=hint,
            provenance=result.provenance,
            retrieved_at=result.retrieved_at,
        )

    # -- status ------------------------------------------------------------

    async def status(self) -> dict[str, Any]:
        """What ``source_status`` reports: reachability and the client's own state."""
        reachable = False
        rate_limited_for: float | None = None
        if self._quota_exhausted_since is None:
            try:
                await self._call("GET", "/status")
                reachable = True
            except RateLimitedError as exc:
                # Not an outage: the source (or our own brake) asked for a
                # pause. Reported as such rather than as «unreachable».
                rate_limited_for = exc.retry_after
                logger.warning("status_rate_limited", seconds=round(exc.retry_after))
            except DiscoverSwissError as exc:
                logger.warning("status_unreachable", reason=type(exc).__name__)
            except net.EgressError as exc:
                logger.error("status_egress_blocked", reason=str(exc))

        return {
            "reachable": reachable,
            "rate_limited_for": rate_limited_for,
            "search_available": self.search_available,
            "project": self._settings.project,
            "base_url": self._settings.base_url,
            "calls_last_minute": self._bucket.calls_last_minute,
            "quota_exhausted_since": self._quota_exhausted_since,
            "last_success": self._last_success,
            "cache_entries": self._cache.live_entries(),
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        # Goes through `safe_summary()` so the key cannot leak into a traceback.
        summary: dict[str, Any] = dict(self._settings.safe_summary())
        return f"DiscoverSwissClient({summary})"


def _parse_json(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text[:500]


def _requested_facet_names(facets: Any) -> list[str]:
    """The response keys a facet request asks for.

    ``FacetRequest.key`` overrides the key the answer is filed under; without
    it the facet name is the key. Comparing against the wrong one would report
    a facet as missing that arrived under its custom name.
    """
    if not isinstance(facets, list):
        return []
    names: list[str] = []
    for facet in facets:
        if isinstance(facet, dict):
            candidate = facet.get("key") or facet.get("name")
        else:
            candidate = facet
        if isinstance(candidate, str) and candidate and candidate not in names:
            names.append(candidate)
    return names
