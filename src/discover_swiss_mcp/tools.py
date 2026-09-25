"""The four core tools of P2 as pure, testable ``*_impl`` functions.

Each function takes the shared :class:`DiscoverSwissClient` and a validated
input model and returns a response envelope. Nothing in here knows about MCP:
the wrappers in :mod:`discover_swiss_mcp.server` add the protocol layer, and
the tests drive these functions directly against recorded shapes.

**Where this file departs from the P2 brief, and why.** The brief was written
before every field was checked against the spec. Where the two disagree, the
spec and the probe win (session rule: the probe is the truth):

* ``license`` is not a field of ``IndexResponse``, so it cannot be in a search
  ``select`` — asking for it answers 400 (probe, PROBE_DETAIL b). The licence of
  a search hit comes from ``dataGovernance`` (see :mod:`licenses`).
* ``priceRange`` is an integer filter (``1``/``2``/``3``); «Niedrig», «Mittel»,
  «Hoch» are the facet's display names (``search_facets.json``). The tool
  accepts the names and sends the integers.
* ``sourcePartner`` filters by partner **acronym** (spec: "source partners
  acronyms"; facet values ``pi`` and ``okgo``), not by display name.
* ``IndexResponse`` has no ``numberOfRooms``, ``priceRange``, ``accessibility``
  or ``season``. A search hit therefore cannot carry room counts, price range,
  accessibility profile names or a tour's season; those fields are not
  invented here. ``get_details`` has rooms and profiles.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from discover_swiss_mcp.client import (
    SEARCH_SELECT_FIELDS,
    AreaLookup,
    DiscoverSwissClient,
    DiscoverSwissError,
    SearchResult,
    UpstreamRejectedError,
    distance_km,
)
from discover_swiss_mcp.licenses import (
    Attribution,
    attribution,
    is_no_derivatives,
    is_servable,
    license_of,
    screen,
)
from discover_swiss_mcp.models import Envelope
from discover_swiss_mcp.transform import html_to_text, trim_detail

Lang = Literal["de", "fr", "it", "en"]

MAX_PAGE_SIZE = 50
TEASER_MAX_CHARS = 200

# The search `select` for the tools: the fields a hit is built from, and not
# one more. Every entry is in the verified 46-field whitelist
# (`client.SEARCH_SELECT_FIELDS`); a test holds that. `time` is here because
# `find_tours` reports a duration, `license` is not because `IndexResponse`
# has no such field and asking for it answers 400.
TOOL_SELECT_FIELDS: tuple[str, ...] = (
    "identifier",
    "name",
    "type",
    "additionalType",
    "address",
    "geo",
    "openingHours",
    "image",
    "disambiguatingDescription",
    "dataGovernance",
    "lastModified",
    "link",
    "starRating",
    "rating",
    "length",
    "elevation",
    "time",
    "nextOccurrence",
    "priceInformation",
    "relevanceScore",
)
TOOL_SELECT = ",".join(TOOL_SELECT_FIELDS)
assert set(TOOL_SELECT_FIELDS) <= set(SEARCH_SELECT_FIELDS)

# Types that `search` leaves out unless `types` asks for them. Rooms carry
# `type: Accommodation`; meeting rooms `additionalType: MeetingRoom`, facet
# display name «Besprechungsraum» (search_facets.json, leafType).
DEFAULT_EXCLUDED_TYPES = frozenset({"Accommodation"})
DEFAULT_EXCLUDED_LEAF_TYPES = frozenset({"MeetingRoom", "Besprechungsraum", "HotelRoom"})

# Facet value → integer the `priceRange` filter takes (search_facets.json).
PRICE_RANGE_CODES: dict[str, int] = {"Niedrig": 1, "Mittel": 2, "Hoch": 3}

# Acronyms of the two partners whose data carries accessibility profiles
# (facet `sourcePartner`: `pi` Pro Infirmis 1'049, `okgo` OK:GO 401).
ACCESSIBILITY_PARTNERS: tuple[str, ...] = ("pi", "okgo")
# Origins in `dataGovernance` that deliver accessibility data. Hotel Du Nord's
# profiles arrive through `gin` (Ginto), the platform Pro Infirmis publishes on.
ACCESSIBILITY_ORIGINS = frozenset({"gin", "pi", "okgo"})

# Star values the `starRatingValue` filter is ORed over. HotellerieSuisse
# classifies in whole stars plus «superior»; half steps are included so a
# source that does use them is not cut off by the filter.
STAR_VALUES: tuple[float, ...] = tuple(x / 2 for x in range(2, 11))

TourKind = Literal["hiking", "cycling", "mtb", "winter", "theme", "all"]

# `kind` → leafType values (`leafType` holds additionalType, else type).
TOUR_KINDS: dict[str, list[str]] = {
    "hiking": ["HikingTrail", "Route", "NatureTrail", "ThemeTrail"],
    "cycling": ["CyclingRoute"],
    "mtb": ["MountainBikeRoute"],
    "winter": ["CrossCountry", "TobogganRun", "SnowshoeTrail"],
    "theme": ["ThemeTrail", "NatureTrail"],
}

# Facet values of `season` (search_facets.json).
SEASON_CODES: tuple[str, ...] = (
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
)

# ---------------------------------------------------------------------------
# Hints (mcp-data-fidelity: an empty result always says what to try next)
# ---------------------------------------------------------------------------

SEARCH_EMPTY_HINT = (
    "No hit. Try: (1) match='all' if you used 'name' — descriptions are indexed too; "
    "(2) drop `types`; (3) use `near` instead of `locality` — locality must match the "
    "address field exactly; (4) call explore_area to see what exists in this region. "
    "Coverage for POIs is Zurich, Eastern Switzerland, Liechtenstein and Engadin; hotels "
    "are nationwide. Do not conclude a place is absent from one empty result."
)

ACCOMMODATION_EMPTY_HINT = (
    "No lodging matched. Relax filters one at a time (amenities first, then stars), widen "
    "`near`, or drop `accessible` — accessibility profiles exist for ~1'000 of 5'275 hotels. "
    "Hotels are covered nationwide; if a town returns nothing, check `locality` spelling "
    "against the address field or use `near`."
)

TOURS_EMPTY_HINT = (
    "No tour matched. Coverage: Eastern Switzerland (Glarnerland, St. Gallen, Thurgau, "
    "Appenzell, Toggenburg, Heidiland), Zurich region, Liechtenstein, Engadin Scuol — 223 "
    "tours in total. There are NO tours for Bernese Oberland, Valais, Ticino or Central "
    "Switzerland in this source; say that, and point to SchweizMobil (schweizmobil.ch) or "
    "the swiss-tourism-mcp server for federal route data. Relax `difficulty_max`/"
    "`length_km_max` before concluding."
)

UNKNOWN_IDENTIFIER_HINT = (
    "Unknown identifier. Identifiers come from search hits (e.g. civ_px9-s28_bggg). "
    "Do not construct them."
)

REMOVED_HINT = "Object was removed upstream; data may be stale."

WITHHELD_LICENSE_HINT = (
    "The provider publishes this object under «{license}», which is not an open licence. "
    "Its content is withheld; name it and link to the provider, do not describe it."
)

DEGRADED_HINTS: dict[str, str] = {
    "quota_exhausted": (
        "The monthly discover.swiss quota of this server is exhausted; no data can be "
        "fetched until it resets. Tell the user the source is unavailable — do not answer "
        "from memory as if it came from discover.swiss."
    ),
    "upstream_unreachable": (
        "discover.swiss did not answer. This says nothing about whether matching objects "
        "exist; tell the user the source is temporarily unreachable and offer to retry."
    ),
    "search_unavailable": (
        "discover.swiss refused its search endpoint for this key. No result was computed, "
        "so absence cannot be inferred; tell the user the search is unavailable."
    ),
}

# Disclaimer variant B (docs/HOUSEKEEPING_P3.md, section 3).
DISCLAIMER_B: dict[str, str] = {
    "de": (
        "Angaben von {provider} via discover.swiss, Stand {date}. Öffnungszeiten und Preise "
        "ohne Gewähr — vor dem Besuch beim Anbieter prüfen."
    ),
    "fr": (
        "Informations de {provider} via discover.swiss, état au {date}. Horaires et prix sans "
        "garantie — à vérifier auprès du prestataire avant la visite."
    ),
    "it": (
        "Informazioni di {provider} via discover.swiss, stato al {date}. Orari e prezzi senza "
        "garanzia — verificare presso il fornitore prima della visita."
    ),
    "en": (
        "Information from {provider} via discover.swiss, as of {date}. Opening hours and prices "
        "without guarantee — check with the provider before visiting."
    ),
}
_UNKNOWN_DATE = {"de": "unbekannt", "fr": "inconnu", "it": "sconosciuto", "en": "unknown"}


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class GeoPoint(BaseModel):
    """A WGS84 coordinate."""

    model_config = ConfigDict(extra="forbid")

    lat: float = Field(..., ge=-90, le=90, description="Latitude, WGS84 (e.g. 47.3779).")
    lon: float = Field(..., ge=-180, le=180, description="Longitude, WGS84 (e.g. 8.5403).")


class _PagedInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    page: int = Field(default=1, ge=1, le=1000, description="1-based result page.")
    page_size: int = Field(
        default=10, ge=1, le=MAX_PAGE_SIZE, description="Hits per page, at most 50."
    )
    lang: Lang = Field(
        default="de",
        description="Language of names and texts (de, fr, it, en). Sent as Accept-Language.",
    )


def _check_radius(near: GeoPoint | None, radius_km: float | None) -> None:
    if radius_km is not None and near is None:
        raise ValueError("`radius_km` needs `near`: a radius is measured from a point.")


class SearchInput(_PagedInput):
    """Full-text and geo search over the whole open index."""

    query: str | None = Field(
        default=None,
        max_length=200,
        description=(
            "Search words. Whole words only: 'Landesmuseum' matches, 'Landesmus' and parts "
            "of compounds do not. Omit to list by type/place alone."
        ),
    )
    types: list[str] | None = Field(
        default=None,
        max_length=20,
        description=(
            "leafType values, ORed: e.g. Hotel, Museum, Restaurant, CafeOrCoffeeShop, "
            "TouristAttraction, ThemeTrail, HikingTrail, Webcam, Event, Playground, Fireplace, "
            "HotelRoom, MeetingRoom. Omitted: all types except rooms and meeting rooms."
        ),
    )
    near: GeoPoint | None = Field(
        default=None,
        description=(
            "Rank hits by distance from this point; each hit then carries distance_km. "
            "With `query`, text relevance outweighs distance in the ranking."
        ),
    )
    radius_km: float | None = Field(
        default=None,
        gt=0,
        le=200,
        description=(
            "Only with `near`: keep hits within this many km. Omitted: no cut-off, "
            "distance only ranks."
        ),
    )
    locality: str | None = Field(
        default=None,
        max_length=100,
        description=(
            "Exact municipality name as written in the address (e.g. 'Zürich', 'Interlaken'). "
            "No fuzzy match."
        ),
    )
    match: Literal["all", "name"] = Field(
        default="all",
        description="'all': query matches name and descriptions. 'name': name only.",
    )

    @model_validator(mode="after")
    def _radius_needs_near(self) -> SearchInput:
        _check_radius(self.near, self.radius_km)
        return self


class GetDetailsInput(BaseModel):
    """One object by identifier."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    identifier: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Identifier from a search hit, e.g. 'civ_px9-s28_bggg'.",
    )
    lang: Lang = Field(default="de", description="Language of texts (de, fr, it, en).")


class FindAccommodationInput(_PagedInput):
    """Lodging search with hotel-specific filters."""

    near: GeoPoint | None = Field(
        default=None, description="Rank by distance from this point. `near` or `locality` needed."
    )
    radius_km: float | None = Field(
        default=None, gt=0, le=200, description="Only with `near`: cut-off radius in km."
    )
    locality: str | None = Field(
        default=None,
        max_length=100,
        description="Exact municipality name from the address, e.g. 'Grindelwald'.",
    )
    stars_min: float | None = Field(
        default=None, ge=1, le=5, description="Minimum HotellerieSuisse stars (1–5)."
    )
    garni: bool | None = Field(
        default=None, description="true: garni only (no restaurant); false: garni excluded."
    )
    price_range: Literal["Niedrig", "Mittel", "Hoch"] | None = Field(
        default=None, description="Provider-declared price band: Niedrig, Mittel or Hoch."
    )
    amenities: list[str] | None = Field(
        default=None,
        max_length=10,
        description=(
            "Amenity feature names, ORed (e.g. 'WiFi', 'Parkplatz', 'Haustierfreundlich')."
        ),
    )
    accessible: bool = Field(
        default=False,
        description=(
            "true: only lodgings with an accessibility profile from Pro Infirmis or OK:GO."
        ),
    )

    @model_validator(mode="after")
    def _place_required(self) -> FindAccommodationInput:
        if self.near is None and not self.locality:
            raise ValueError("Give `near` or `locality`: lodging search is always local.")
        _check_radius(self.near, self.radius_km)
        return self


class FindToursInput(_PagedInput):
    """Tour search with tour-specific filters."""

    near: GeoPoint | None = Field(default=None, description="Rank by distance from this point.")
    radius_km: float | None = Field(
        default=None, gt=0, le=200, description="Only with `near`: cut-off radius in km."
    )
    locality: str | None = Field(
        default=None, max_length=100, description="Exact municipality name from the address."
    )
    region: str | None = Field(
        default=None,
        max_length=100,
        description="Area name, exact (e.g. 'Glarnerland', 'Toggenburg'); resolved to an area id.",
    )
    kind: TourKind = Field(
        default="all",
        description=(
            "hiking (hiking trails, routes, nature and theme trails), cycling, mtb, "
            "winter (cross-country, toboggan runs, snowshoe trails), theme, or all."
        ),
    )
    difficulty_max: int | None = Field(
        default=None, ge=1, le=3, description="Highest difficulty: 1 easy, 2 medium, 3 hard."
    )
    length_km_max: float | None = Field(default=None, gt=0, le=500, description="Maximum km.")
    ascent_m_max: int | None = Field(
        default=None, ge=0, le=10000, description="Maximum ascent in metres."
    )
    season_month: int | None = Field(
        default=None, ge=1, le=12, description="Month the tour is recommended for (1–12)."
    )

    @model_validator(mode="after")
    def _radius_needs_near(self) -> FindToursInput:
        _check_radius(self.near, self.radius_km)
        return self


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------


class Hit(BaseModel):
    """One search hit, reduced to what answers a guest question."""

    identifier: str
    name: str | None = None
    type: str | None = None
    leaf_type: str | None = None
    locality: str | None = None
    distance_km: float | None = None
    teaser: str | None = None
    opening_hours: str | None = None
    image_url: str | None = None
    website: str | None = None
    last_modified: str | None = None
    attribution: Attribution


class AccommodationHit(Hit):
    stars: float | None = None
    garni: bool | None = None
    superior: bool | None = None
    # Providers in this object's data governance that deliver accessibility
    # data (Ginto, Pro Infirmis, OK:GO). The profile names themselves are not in
    # the search index; `get_details` returns them.
    accessibility_sources: list[str] = Field(default_factory=list)


class TourHit(Hit):
    length_km: float | None = None
    ascent_m: int | None = None
    descent_m: int | None = None
    difficulty: int | None = None
    duration_min: int | None = None
    provider: str | None = None


class _PagedResponse(Envelope):
    # `count` from upstream, before any filtering — across all pages.
    upstream_count: int | None = None
    # Hits upstream delivered for this page; returned + the three excluded
    # counters add up to it.
    fetched: int = 0
    # Hits in this response, after filtering.
    returned: int = 0
    page: int = 1
    page_size: int = 10
    has_more: bool = False
    # The scope actually sent upstream, so the model can see what it asked.
    applied: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(_PagedResponse):
    hits: list[Hit] = Field(default_factory=list)


class AccommodationResponse(_PagedResponse):
    hits: list[AccommodationHit] = Field(default_factory=list)


class AreaInfo(BaseModel):
    query: str
    identifier: str | None = None
    name: str | None = None
    ambiguous: bool = False
    note: str | None = None


class ToursResponse(_PagedResponse):
    area: AreaInfo | None = None
    hits: list[TourHit] = Field(default_factory=list)


class DetailResponse(Envelope):
    identifier: str
    name: str | None = None
    license: str | None = None
    removed: bool = False
    # True for CC BY-ND: quote or summarise facts, never rewrite the text.
    no_derivatives: bool = False
    attribution: Attribution | None = None
    detail: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(UTC)


def _short_type(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return value.removeprefix("schema.org/")


def _str_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _coords(obj: dict[str, Any]) -> tuple[float, float] | None:
    geo = obj.get("geo")
    if not isinstance(geo, dict):
        return None
    try:
        return float(geo["latitude"]), float(geo["longitude"])
    except (KeyError, TypeError, ValueError):
        return None


def _teaser(obj: dict[str, Any]) -> str | None:
    text = html_to_text(obj.get("disambiguatingDescription"))
    if text is None:
        return None
    text = " ".join(text.split())
    if len(text) <= TEASER_MAX_CHARS:
        return text
    cut = text[: TEASER_MAX_CHARS - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + "…"


def _image_url(obj: dict[str, Any]) -> str | None:
    image = obj.get("image")
    if isinstance(image, dict):
        return _str_or_none(image.get("contentUrl"))
    return None


def is_default_excluded(obj: dict[str, Any]) -> bool:
    """Whether ``search`` drops this hit when ``types`` is not given."""
    if _short_type(obj.get("type")) in DEFAULT_EXCLUDED_TYPES:
        return True
    return _short_type(obj.get("additionalType")) in DEFAULT_EXCLUDED_LEAF_TYPES


def _hit_fields(obj: dict[str, Any], near: GeoPoint | None) -> dict[str, Any]:
    address = obj.get("address") if isinstance(obj.get("address"), dict) else {}
    distance = None
    if near is not None:
        coords = _coords(obj)
        if coords is not None:
            distance = round(distance_km(near.lat, near.lon, coords[0], coords[1]), 2)
    credit = attribution(obj)
    return {
        "identifier": str(obj.get("identifier") or ""),
        "name": _str_or_none(obj.get("name")),
        "type": _short_type(obj.get("type")),
        "leaf_type": _short_type(obj.get("additionalType")) or _short_type(obj.get("type")),
        "locality": _str_or_none(address.get("addressLocality")),
        "distance_km": distance,
        "teaser": _teaser(obj),
        "opening_hours": html_to_text(obj.get("openingHours")),
        "image_url": _image_url(obj),
        "website": credit.source_url,
        "last_modified": _str_or_none(obj.get("lastModified")),
        "attribution": credit,
    }


def _freshness(objects: list[dict[str, Any]]) -> str | None:
    stamps = [obj.get("lastModified") for obj in objects]
    stamps = [s for s in stamps if isinstance(s, str) and s]
    return max(stamps) if stamps else None


def geo_distance_filter(near: GeoPoint, radius_km: float) -> str:
    """The OData radius filter, verified live (PROBE_VERIFY 3). Longitude first."""
    return f"geo.distance(geo, geography'POINT({near.lon} {near.lat})') le {radius_km}"


def scoring_point(near: GeoPoint) -> str:
    """``Longitude,Latitude`` — the order the spec names, and easy to get wrong."""
    return f"{near.lon},{near.lat}"


def _format_date(stamp: str | None, lang: str) -> str:
    if not stamp:
        return _UNKNOWN_DATE.get(lang, _UNKNOWN_DATE["en"])
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return stamp[:10]
    if lang == "en":
        return moment.date().isoformat()
    return moment.strftime("%d.%m.%Y")


def disclaimer_b(providers: list[str], last_modified: str | None, lang: str) -> str:
    """Disclaimer variant B, filled with provider(s) and date, in ``lang``."""
    names = [p for p in dict.fromkeys(providers) if p and p != "unknown"]
    provider = ", ".join(names) if names else "discover.swiss"
    template = DISCLAIMER_B.get(lang, DISCLAIMER_B["en"])
    return template.format(provider=provider, date=_format_date(last_modified, lang))


def _paged_hint(
    upstream_count: int | None,
    fetched: int,
    returned: int,
    page: int,
    empty_hint: str,
    *,
    by_license: int = 0,
    test_objects: int = 0,
    default_types: int = 0,
) -> str | None:
    """The hint for a page that came back short of hits.

    Three different empties, three different messages: nothing matched at all,
    the page is past the end, and everything on the page was withheld. Folding
    them into one would tell the model to relax filters when the answer is
    something else. The withheld case names each reason with its count, and
    only suggests `types` when rooms are actually among them — advice that
    does not fit the page sends a model paging through the whole index.
    """
    if returned > 0:
        return None
    if fetched > 0:
        reasons = []
        if by_license:
            reasons.append(f"{by_license} not openly licensed (they may not be shown or described)")
        if test_objects:
            reasons.append(f"{test_objects} test records")
        if default_types:
            reasons.append(f"{default_types} rooms/meeting rooms (pass `types` to include them)")
        detail = "; ".join(reasons) if reasons else "see the excluded_* counters"
        more = (
            " Later pages may still hold servable hits."
            if upstream_count is not None and upstream_count > fetched * page
            else ""
        )
        return f"All {fetched} hits on this page were withheld: {detail}.{more}"
    if upstream_count and page > 1:
        return (
            f"Page {page} is past the end: {upstream_count} hits in total. Request an earlier page."
        )
    return empty_hint


def degraded_envelope_fields(exc: DiscoverSwissError) -> dict[str, Any]:
    """Envelope fields for a failure that is a *state*, not a bug."""
    return {
        "provenance": "live_api",
        "retrieved_at": _now(),
        "source_freshness": None,
        "degraded": exc.degraded,
        "hint": DEGRADED_HINTS.get(exc.degraded or "", str(exc)),
    }


async def _run_search(
    client: DiscoverSwissClient, body: dict[str, Any], lang: str
) -> SearchResult | DiscoverSwissError:
    """Call ``/search``; a degraded state comes back as a value, anything else raises."""
    try:
        return await client.search(body, lang=lang)
    except DiscoverSwissError as exc:
        if exc.degraded is None:
            raise
        return exc


def _paging(
    result: SearchResult, page: int, page_size: int, fetched: int
) -> tuple[int | None, bool]:
    count = result.count
    has_more = count is not None and page * page_size < count
    if count is None:
        # Without a count, a full page is the only sign that another may follow.
        has_more = fetched >= page_size
    return count, has_more


# ---------------------------------------------------------------------------
# Tool 1 — search
# ---------------------------------------------------------------------------


def build_search_body(params: SearchInput) -> dict[str, Any]:
    body: dict[str, Any] = {
        "searchText": params.query,
        "searchFields": "name" if params.match == "name" and params.query else None,
        "leafType": list(params.types) if params.types else None,
        "addressLocality": [params.locality] if params.locality else None,
        "scoringReferencePoint": scoring_point(params.near) if params.near else None,
        "filters": (
            [geo_distance_filter(params.near, params.radius_km)]
            if params.near is not None and params.radius_km is not None
            else None
        ),
        "resultsPerPage": params.page_size,
        "currentPage": params.page,
        "select": TOOL_SELECT,
    }
    return {k: v for k, v in body.items() if v is not None}


async def search_impl(client: DiscoverSwissClient, params: SearchInput) -> SearchResponse:
    body = build_search_body(params)
    applied = {k: v for k, v in body.items() if k != "select"}
    applied["default_type_exclusion"] = params.types is None
    project = client.settings.project

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return SearchResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            applied=applied,
            **degraded_envelope_fields(result),
        )

    screened = screen(result.values)
    kept = screened.kept
    excluded_default = 0
    if params.types is None:
        before = len(kept)
        kept = [obj for obj in kept if not is_default_excluded(obj)]
        excluded_default = before - len(kept)

    hits = [Hit(**_hit_fields(obj, params.near)) for obj in kept]
    fetched = len(result.values)
    upstream_count, has_more = _paging(result, params.page, params.page_size, fetched)
    return SearchResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        source_freshness=_freshness(kept),
        project=project,
        hint=_paged_hint(
            upstream_count,
            fetched,
            len(hits),
            params.page,
            SEARCH_EMPTY_HINT,
            by_license=screened.excluded_by_license,
            test_objects=screened.excluded_test_objects,
            default_types=excluded_default,
        ),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        excluded_by_default_types=excluded_default,
        upstream_count=upstream_count,
        fetched=fetched,
        returned=len(hits),
        page=params.page,
        page_size=params.page_size,
        has_more=has_more,
        applied=applied,
        hits=hits,
    )


# ---------------------------------------------------------------------------
# Tool 2 — get_details
# ---------------------------------------------------------------------------


async def get_details_impl(client: DiscoverSwissClient, params: GetDetailsInput) -> DetailResponse:
    project = client.settings.project
    identifier = params.identifier
    cached = client.is_vertex_cached(identifier, params.lang)

    try:
        obj = await client.get_vertex(identifier, lang=params.lang)
    except UpstreamRejectedError:
        # The identifier failed the client's shape gate: nothing was sent, and
        # to the model this is the same situation as a 404.
        obj = None
    except DiscoverSwissError as exc:
        if exc.degraded is None:
            raise
        return DetailResponse(
            identifier=identifier, project=project, **degraded_envelope_fields(exc)
        )

    retrieved_at = _now()
    provenance = "cached" if cached else "live_api"

    if obj is None:
        return DetailResponse(
            identifier=identifier,
            project=project,
            provenance=provenance,
            retrieved_at=retrieved_at,
            source_freshness=None,
            hint=UNKNOWN_IDENTIFIER_HINT,
        )

    credit = attribution(obj)
    licence = license_of(obj)
    last_modified = _str_or_none(obj.get("lastModified"))
    name = _str_or_none(obj.get("name"))

    if not is_servable(obj):
        return DetailResponse(
            identifier=identifier,
            name=name,
            license=licence,
            attribution=credit,
            project=project,
            provenance=provenance,
            retrieved_at=retrieved_at,
            source_freshness=last_modified,
            excluded_by_license=1,
            hint=WITHHELD_LICENSE_HINT.format(license=licence or "none"),
        )

    removed = obj.get("removed") is True
    return DetailResponse(
        identifier=identifier,
        name=name,
        license=licence,
        removed=removed,
        no_derivatives=is_no_derivatives(obj),
        attribution=credit,
        detail=trim_detail(obj, params.lang),
        project=project,
        provenance=provenance,
        retrieved_at=retrieved_at,
        source_freshness=last_modified,
        disclaimer=disclaimer_b([credit.provider], last_modified, params.lang),
        hint=REMOVED_HINT if removed else None,
    )


# ---------------------------------------------------------------------------
# Tool 3 — find_accommodation
# ---------------------------------------------------------------------------


def build_accommodation_body(params: FindAccommodationInput) -> dict[str, Any]:
    body: dict[str, Any] = {
        "type": ["LodgingBusiness"],
        "addressLocality": [params.locality] if params.locality else None,
        "scoringReferencePoint": scoring_point(params.near) if params.near else None,
        "filters": (
            [geo_distance_filter(params.near, params.radius_km)]
            if params.near is not None and params.radius_km is not None
            else None
        ),
        "starRatingValue": (
            [v for v in STAR_VALUES if v >= params.stars_min]
            if params.stars_min is not None
            else None
        ),
        "starRatingGarni": [params.garni] if params.garni is not None else None,
        "priceRange": [PRICE_RANGE_CODES[params.price_range]] if params.price_range else None,
        "amenityFeature": list(params.amenities) if params.amenities else None,
        "sourcePartner": list(ACCESSIBILITY_PARTNERS) if params.accessible else None,
        "resultsPerPage": params.page_size,
        "currentPage": params.page,
        "select": TOOL_SELECT,
    }
    return {k: v for k, v in body.items() if v is not None}


def _accessibility_sources(obj: dict[str, Any]) -> list[str]:
    governance = obj.get("dataGovernance")
    if not isinstance(governance, dict) or not isinstance(governance.get("origin"), list):
        return []
    names: list[str] = []
    for origin in governance["origin"]:
        if not isinstance(origin, dict) or not isinstance(origin.get("provider"), dict):
            continue
        provider = origin["provider"]
        acronym = str(provider.get("acronym") or provider.get("identifier") or "").lower()
        name = provider.get("name")
        if acronym in ACCESSIBILITY_ORIGINS and isinstance(name, str) and name not in names:
            names.append(name)
    return names


def _accommodation_hit(obj: dict[str, Any], near: GeoPoint | None) -> AccommodationHit:
    rating = obj.get("starRating") if isinstance(obj.get("starRating"), dict) else {}
    stars = rating.get("ratingValue")
    return AccommodationHit(
        **_hit_fields(obj, near),
        stars=float(stars)
        if isinstance(stars, int | float) and not isinstance(stars, bool)
        else None,
        garni=rating.get("garni") if isinstance(rating.get("garni"), bool) else None,
        superior=rating.get("superior") if isinstance(rating.get("superior"), bool) else None,
        accessibility_sources=_accessibility_sources(obj),
    )


async def find_accommodation_impl(
    client: DiscoverSwissClient, params: FindAccommodationInput
) -> AccommodationResponse:
    body = build_accommodation_body(params)
    applied = {k: v for k, v in body.items() if k != "select"}
    project = client.settings.project

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return AccommodationResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            applied=applied,
            **degraded_envelope_fields(result),
        )

    screened = screen(result.values)
    hits = [_accommodation_hit(obj, params.near) for obj in screened.kept]
    fetched = len(result.values)
    upstream_count, has_more = _paging(result, params.page, params.page_size, fetched)
    freshness = _freshness(screened.kept)
    return AccommodationResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        source_freshness=freshness,
        project=project,
        disclaimer=(
            disclaimer_b([h.attribution.provider for h in hits], freshness, params.lang)
            if hits
            else None
        ),
        hint=_paged_hint(
            upstream_count,
            fetched,
            len(hits),
            params.page,
            ACCOMMODATION_EMPTY_HINT,
            by_license=screened.excluded_by_license,
            test_objects=screened.excluded_test_objects,
        ),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        upstream_count=upstream_count,
        fetched=fetched,
        returned=len(hits),
        page=params.page,
        page_size=params.page_size,
        has_more=has_more,
        applied=applied,
        hits=hits,
    )


# ---------------------------------------------------------------------------
# Tool 4 — find_tours
# ---------------------------------------------------------------------------


def tour_filters(params: FindToursInput) -> str | None:
    """The OData conditions, joined with ``and`` — the combined form verified live."""
    parts: list[str] = []
    if params.length_km_max is not None:
        # `length` is metres upstream (PROBE_VERIFY 2: `length le 10000` = 10 km).
        parts.append(f"length le {round(params.length_km_max * 1000)}")
    if params.ascent_m_max is not None:
        parts.append(f"elevation/ascent le {params.ascent_m_max}")
    if params.difficulty_max is not None:
        parts.append(f"rating/difficulty le {params.difficulty_max}")
    if params.near is not None and params.radius_km is not None:
        parts.append(geo_distance_filter(params.near, params.radius_km))
    return " and ".join(parts) if parts else None


def build_tours_body(params: FindToursInput, area_id: str | None) -> dict[str, Any]:
    conditions = tour_filters(params)
    body: dict[str, Any] = {
        "type": ["Tour"],
        "leafType": TOUR_KINDS.get(params.kind),
        "containedInPlace": [area_id] if area_id else None,
        "addressLocality": [params.locality] if params.locality else None,
        "scoringReferencePoint": scoring_point(params.near) if params.near else None,
        "filters": [conditions] if conditions else None,
        "season": [SEASON_CODES[params.season_month - 1]] if params.season_month else None,
        "resultsPerPage": params.page_size,
        "currentPage": params.page,
        "select": TOOL_SELECT,
    }
    return {k: v for k, v in body.items() if v is not None}


def _tour_hit(obj: dict[str, Any], near: GeoPoint | None) -> TourHit:
    fields = _hit_fields(obj, near)
    length = obj.get("length")
    elevation = obj.get("elevation") if isinstance(obj.get("elevation"), dict) else {}
    rating = obj.get("rating") if isinstance(obj.get("rating"), dict) else {}
    return TourHit(
        **fields,
        length_km=(
            round(float(length) / 1000, 1)
            if isinstance(length, int | float) and not isinstance(length, bool) and length > 0
            else None
        ),
        ascent_m=_int_or_none(elevation.get("ascent")),
        descent_m=_int_or_none(elevation.get("descent")),
        difficulty=_int_or_none(rating.get("difficulty")),
        duration_min=_int_or_none(obj.get("time")),
        provider=fields["attribution"].provider,
    )


def _area_info(lookup: AreaLookup) -> AreaInfo:
    return AreaInfo(
        query=lookup.query,
        identifier=lookup.identifier,
        name=lookup.name,
        ambiguous=lookup.ambiguous,
        note=lookup.hint,
    )


async def find_tours_impl(client: DiscoverSwissClient, params: FindToursInput) -> ToursResponse:
    project = client.settings.project
    area: AreaInfo | None = None
    area_id: str | None = None

    if params.region:
        try:
            lookup = await client.resolve_area(params.region, lang=params.lang)
        except DiscoverSwissError as exc:
            if exc.degraded is None:
                raise
            return ToursResponse(
                project=project,
                page=params.page,
                page_size=params.page_size,
                **degraded_envelope_fields(exc),
            )
        area = _area_info(lookup)
        if lookup.identifier is None:
            # An unresolved area must not fall through to an unfiltered search:
            # 223 tours from everywhere would read as "tours in this region".
            return ToursResponse(
                project=project,
                provenance=lookup.provenance,
                retrieved_at=lookup.retrieved_at,
                source_freshness=None,
                page=params.page,
                page_size=params.page_size,
                area=area,
                hint=(
                    f"{lookup.hint} Pass one of these names as `region`, or use `near` "
                    "with a coordinate instead. No tour search was run."
                ),
            )
        area_id = lookup.identifier

    body = build_tours_body(params, area_id)
    applied = {k: v for k, v in body.items() if k != "select"}

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return ToursResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            applied=applied,
            area=area,
            **degraded_envelope_fields(result),
        )

    screened = screen(result.values)
    hits = [_tour_hit(obj, params.near) for obj in screened.kept]
    fetched = len(result.values)
    upstream_count, has_more = _paging(result, params.page, params.page_size, fetched)
    return ToursResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        source_freshness=_freshness(screened.kept),
        project=project,
        hint=_paged_hint(
            upstream_count,
            fetched,
            len(hits),
            params.page,
            TOURS_EMPTY_HINT,
            by_license=screened.excluded_by_license,
            test_objects=screened.excluded_test_objects,
        ),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        upstream_count=upstream_count,
        fetched=fetched,
        returned=len(hits),
        page=params.page,
        page_size=params.page_size,
        has_more=has_more,
        applied=applied,
        area=area,
        hits=hits,
    )
