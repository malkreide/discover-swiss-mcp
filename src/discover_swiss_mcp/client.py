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

from discover_swiss_mcp import __version__, net
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

# List-endpoint `select`. Exactly the nine fields the probe sent and got back on
# every content endpoint. Shorter than the search whitelist on purpose: the list
# endpoints each have their own response definition, so a field that is fine on
# `/lodgingbusinesses` may 400 on `/webcams`. Adding one is a live check, not a
# guess — and `select` matters: omitting it costs ~9.5 KB per object instead of
# ~1 KB.
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

# A 429 names its own wait («Try again in N seconds»), and that wait is allowed
# to run past `TOTAL_BUDGET`: the budget guards against an upstream that has
# stopped answering, and a 429 is the opposite — the source saying exactly when
# it will answer again. Sitting out a named wait beats spending the call on a
# failure. The cap is where that stops being true: beyond 30 s the MCP client
# has given up first, so the call fails immediately instead, with the seconds in
# the message so the tool can say «try again in N seconds» rather than «error».
RATE_LIMIT_MAX_WAIT = 30.0

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

# Indirection so tests can null the waiting without patching `asyncio.sleep`
# itself. Patching the stdlib function looks local and is not: it silences
# every sleep in the process, including those of unrelated tests that then hand
# the event loop the floor and measure nothing.
_sleep = asyncio.sleep


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class DiscoverSwissError(RuntimeError):
    """Base class. ``degraded`` is the value the tool puts in the envelope."""

    degraded: str | None = None


class UpstreamUnavailableError(DiscoverSwissError):
    """Network failure, timeout, or 5xx that survived the retry ladder."""

    degraded = "upstream_unreachable"


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
    """The result of resolving an area name to an area id."""

    query: str
    identifier: str | None = None
    name: str | None = None
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
        self._prune(time.monotonic())
        return len(self._stamps)

    async def acquire(self) -> None:
        """Wait, if needed, until a call fits inside the window."""
        async with self._lock:
            now = time.monotonic()
            self._prune(now)
            if len(self._stamps) >= self._limit:
                wait = self._window - (now - self._stamps[0]) + 0.05
                if wait > 0:
                    logger.info("rate_limit_wait", seconds=round(wait, 2))
                    await _sleep(wait)
                self._prune(time.monotonic())
            self._stamps.append(time.monotonic())


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
        if expires_at <= time.monotonic():
            del self._entries[key]
            return None
        self._entries.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        now = time.monotonic()
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

    def __len__(self) -> int:  # pragma: no cover - diagnostics
        return len(self._entries)


def _cache_key(kind: str, lang: str, payload: Any) -> str:
    return f"{kind}|{lang}|{json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)}"


# ---------------------------------------------------------------------------
# Helpers the tools share
# ---------------------------------------------------------------------------


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

    The list responses call it ``count``; the field name is read tolerantly
    anyway, because reading a number out of a live answer is cheaper than being
    wrong about it after a release note nobody saw.
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
    def search_available(self) -> bool:
        """Whether ``/search`` is believed to work right now."""
        if self._search_unavailable_until is None:
            return True
        if time.monotonic() >= self._search_unavailable_until:
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

        deadline = time.monotonic() + TOTAL_BUDGET
        retry_index = 0
        rate_limit_retries = 0

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UpstreamUnavailableError(
                    f"discover.swiss did not answer within {TOTAL_BUDGET:.0f} s."
                )

            await self._bucket.acquire()
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
                if delay >= deadline - time.monotonic():
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
                if rate_limit_retries >= 1 or wait > RATE_LIMIT_MAX_WAIT:
                    raise UpstreamUnavailableError(
                        f"discover.swiss rate limit reached; it asks for {wait:.0f} s."
                    )
                rate_limit_retries += 1
                logger.warning("rate_limited", path=path, seconds=wait)
                # The named wait buys itself room in the budget; see
                # RATE_LIMIT_MAX_WAIT.
                deadline += wait
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
                    self._search_unavailable_until = time.monotonic() + SEARCH_UNAVAILABLE_SECONDS
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
                if delay >= deadline - time.monotonic():
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
        """
        if not self.search_available:
            raise SearchUnavailableError(
                "discover.swiss refused /search recently; the list fallback is the way in."
            )

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

        payload = await self._call(
            "POST", "/search", json_body=request, lang=lang, search_endpoint=True
        )
        payload = payload if isinstance(payload, dict) else {}
        facets = payload.get("facets")
        facets = facets if isinstance(facets, dict) else {}
        missing = [name for name in requested_facets if name not in facets]
        if missing:
            # An unknown facet name is dropped without an error. Logging it is
            # half the job; the other half is `missing_facets` reaching the
            # envelope, so the model is told what it is not seeing.
            logger.warning("facets_missing", requested=requested_facets, missing=missing)

        values = payload.get("values")
        result = SearchResult(
            count=payload.get("count") if isinstance(payload.get("count"), int) else None,
            values=[v for v in values if isinstance(v, dict)] if isinstance(values, list) else [],
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
            raise UpstreamRejectedError(f"{identifier!r} is not a discover.swiss identifier.")

        key = _cache_key("vertex", lang, identifier)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        payload = await self._call(
            "GET",
            f"/vertices/{quote(identifier, safe='')}",
            params={"project": self._settings.project},
            lang=lang,
            allow_404=True,
        )
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise UpstreamRejectedError(
                "discover.swiss returned a detail object that is not an object."
            )
        self._cache.set(key, payload, VERTEX_TTL_SECONDS)
        return payload

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
        payload = payload if isinstance(payload, dict) else {}
        rows = payload.get("data")
        return ListPage(
            data=[r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else [],
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
        """
        result = await self.search(
            {
                "searchText": name,
                "resultsPerPage": 1,
                "select": "identifier",
                "facets": [{"name": "containedInPlace/id", "count": 30}],
            },
            lang=lang,
        )
        values = facet_values(result.facets, "containedInPlace/id")
        wanted = name.strip().casefold()

        for value in values:
            if str(value.get("name", "")).strip().casefold() == wanted:
                return AreaLookup(
                    query=name,
                    identifier=str(value.get("value")),
                    name=str(value.get("name")),
                    provenance=result.provenance,
                    retrieved_at=result.retrieved_at,
                )

        suggestions = [
            AreaSuggestion(
                identifier=str(value.get("value")),
                name=str(value.get("name")),
                count=value.get("count") if isinstance(value.get("count"), int) else None,
            )
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
        if self._quota_exhausted_since is None:
            try:
                await self._call("GET", "/status")
                reachable = True
            except DiscoverSwissError as exc:
                logger.warning("status_unreachable", reason=type(exc).__name__)
            except net.EgressError as exc:
                logger.error("status_egress_blocked", reason=str(exc))

        return {
            "reachable": reachable,
            "search_available": self.search_available,
            "calls_last_minute": self._bucket.calls_last_minute,
            "quota_exhausted_since": self._quota_exhausted_since,
            "last_success": self._last_success,
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
