"""The eight tools as pure, testable ``*_impl`` functions (P2: the first four, P3: the rest).

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

import re
from datetime import UTC, date, datetime, timedelta
from typing import Any, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from discover_swiss_mcp.client import (
    SEARCH_SELECT_FIELDS,
    VERIFIED_FACETS,
    AreaLookup,
    DiscoverSwissClient,
    DiscoverSwissError,
    InvalidIdentifierError,
    SearchResult,
    SearchUnavailableError,
    distance_km,
    facet_request,
    facet_values,
    filter_by_distance,
    partition_facet_names,
)
from discover_swiss_mcp.licenses import (
    Attribution,
    attribution,
    is_no_derivatives,
    is_servable,
    is_test_object,
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

# `kind` → body filter, measured live on 2026-09-25
# (`probes/PROBE_TOURKINDS_discover-swiss.md`). The first mapping guessed
# `CyclingRoute`, `MountainBikeRoute` and `SnowshoeTrail` — none of them exists
# in the index, so three kinds answered with a silent empty set.
#
# Two sources, used where each is complete enough:
# * `leafType` for walking: 178 of 223 tours fall under these seven types.
# * `categoryTree` for winter and cycling, where the types do not separate:
#   the 23 snowshoe tours are filed as `Route`. Only the **full path** filters;
#   the short code (`sui_0110`) answers 0 without an error.
#
# `leafType` and `categoryTree` are ANDed upstream (hiking types AND winter
# category: 25), so a kind cannot be one field OR the other.
HIKING_LEAF_TYPES: list[str] = [
    "HikingTrail",
    "Route",
    "Way",
    "Tour",
    "Longdistance",
    "NatureTrail",
    "ThemeTrail",
]
CATEGORY_WINTER = "sui_root|sui_01|sui_0110"
CATEGORY_CYCLING = "sui_root|sui_01|sui_0102"
CATEGORY_MTB = "sui_root|sui_01|sui_0102|sui_010205"

TOUR_KINDS: dict[str, dict[str, list[str]]] = {
    "hiking": {"leafType": HIKING_LEAF_TYPES},
    "cycling": {"categoryTree": [CATEGORY_CYCLING]},
    "mtb": {"categoryTree": [CATEGORY_MTB]},
    "winter": {"categoryTree": [CATEGORY_WINTER]},
    "theme": {"leafType": ["ThemeTrail", "NatureTrail"]},
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

# What the query-syntax probe (2026-09-26) measured as not understood. Each
# one returns 0 or fewer hits instead of an error, so an empty result after one
# says the query, not the index, is the cause.
_UNSUPPORTED_SYNTAX = re.compile(r"[*?~]|(?:^|\s)-\S|\b(?:AND|OR)\b|\"")


def query_syntax_note(query: str | None) -> str | None:
    """A hint for a query that uses syntax the source does not understand."""
    if not query or not _UNSUPPORTED_SYNTAX.search(query):
        return None
    return (
        "The query uses syntax the source does not understand (wildcards *, ?, fuzzy ~, "
        "AND/OR, '-' exclusion or quotes); it matches whole words only, all of them. "
        "Retry with plain whole words, one search per alternative."
    )


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
    "`length_km_max` before concluding. Drop `season_month` first: it keeps only tours "
    "that declare seasons (20 of 178 walking tours for July)."
)

UNKNOWN_IDENTIFIER_HINT = (
    "Unknown identifier. Identifiers come from search hits (e.g. civ_px9-s28_bggg). "
    "Do not construct them."
)

REMOVED_HINT = "Object was removed upstream; data may be stale."

TEST_OBJECT_HINT = (
    "This object is a test record in the production index (placeholder name or address); its "
    "content is withheld. Do not present it as a real offer."
)

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
    "upstream_shape_changed": (
        "discover.swiss answered in a structure this server does not recognise, so nothing "
        "could be read from it. This is not an empty result — do not conclude that nothing "
        "exists; tell the user the source changed and the server needs an update."
    ),
    "rate_limited": (
        "The call rate is exhausted for the moment; retry in about {seconds} seconds. No "
        "result was computed, so absence cannot be inferred — say the source is busy."
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
            "Whole words, e.g. 'Landesmuseum'; case-insensitive; several words must all "
            "match. No prefixes, wildcards (*, ?), fuzzy (~), AND/OR or '-' exclusion "
            "(measured: they return 0 or fewer hits). Omit to list by type/place alone."
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
            "hiking: walking types (hiking trails, routes, ways, nature and theme trails; "
            "includes snowshoe routes the provider files as routes). winter: snowshoe, "
            "cross-country, sledging by category. cycling / mtb: by category (2 tours). "
            "theme: theme and nature trails. all: no restriction."
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
        default=None,
        ge=1,
        le=12,
        description=(
            "Month the tour is recommended for (1–12). Only tours that declare seasons can "
            "match — most do not."
        ),
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
    # Parameters the caller set that this answer did not apply — the list
    # fallback cannot filter by them. The hits are wider than asked for, and a
    # field says so where a sentence in `hint` could be skimmed (DRIFT-002).
    ignored_parameters: list[str] = Field(default_factory=list)


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
        "hint": DEGRADED_HINTS.get(exc.degraded or "", str(exc)).format(
            seconds=f"{getattr(exc, 'retry_after', 0):.0f}"
        ),
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
# List fallback — the way in when `/search` is refused
# ---------------------------------------------------------------------------

FALLBACK_HINT = (
    "Full-text search is currently unavailable upstream; results come from typed lists "
    "filtered by area and distance."
)

FALLBACK_EMPTY_HINT = (
    "No listed object matched the area and distance. Widen `radius_km`, or check `locality` "
    "against the spelling in the address."
)

# The five collections that hold what `search` and `find_accommodation` serve.
# Lodging last: it is the largest (5'275 rows), and when the call budget runs
# out, the four POI collections are the ones a `search` caller is more likely
# to have meant.
FALLBACK_ENDPOINTS: tuple[str, ...] = (
    "places",
    "civicStructures",
    "foodEstablishments",
    "localbusinesses",
    "lodgingbusinesses",
)

# leafType → the collection that holds it, from the probe's endpoint matrix
# (PROBE_REPORT section 2). A type not listed here scans all five collections
# and is matched client-side — slower, never silently empty.
FALLBACK_TYPE_ENDPOINTS: dict[str, str] = {
    "Hotel": "lodgingbusinesses",
    "LodgingBusiness": "lodgingbusinesses",
    "HolidayApartment": "lodgingbusinesses",
    "Museum": "civicStructures",
    "Theater": "civicStructures",
    "ArtObject": "civicStructures",
    "TouristAttraction": "civicStructures",
    "Restaurant": "foodEstablishments",
    "CafeOrCoffeeShop": "foodEstablishments",
    "Winery": "foodEstablishments",
    "Store": "localbusinesses",
    "SportsActivityLocation": "localbusinesses",
    "NightClub": "localbusinesses",
    "PublicSwimmingPool": "localbusinesses",
    "DaySpa": "localbusinesses",
    "LocalBusiness": "localbusinesses",
    "Place": "places",
    "Lake": "places",
    "Landform": "places",
    "Waterfall": "places",
    "Mountain": "places",
}

# `top=1000` works on the list endpoints (probe run 3) at ~1 KB per row with
# the list `select`, and a Cosmos page cut below that is followed by token.
FALLBACK_TOP = 1000
# Calls one tool call may spend on the fallback. Without an area id the whole
# collection is scanned — 5'275 lodgings are six calls — and eight keeps a
# single question from eating a seventh of the minute's budget.
FALLBACK_MAX_CALLS = 8
# Radius for `near` without `radius_km`. `/search` only ranks then; a list
# cannot rank without cutting somewhere, and the cut is reported in `applied`.
FALLBACK_DEFAULT_RADIUS_KM = 10.0


class _FallbackScan(BaseModel):
    matched: list[dict[str, Any]] = Field(default_factory=list)
    scanned: int = 0
    collection_total: int | None = None
    complete: bool = True
    skipped_endpoints: list[str] = Field(default_factory=list)
    retrieved_at: datetime


def _leaf_types(obj: dict[str, Any]) -> set[str]:
    return {t for t in (_short_type(obj.get("additionalType")), _short_type(obj.get("type"))) if t}


def fallback_endpoints(types: list[str] | None) -> tuple[str, ...]:
    """The collections to scan for ``types`` — all five when any type is unmapped."""
    if not types or any(t not in FALLBACK_TYPE_ENDPOINTS for t in types):
        return FALLBACK_ENDPOINTS
    wanted = {FALLBACK_TYPE_ENDPOINTS[t] for t in types}
    return tuple(e for e in FALLBACK_ENDPOINTS if e in wanted)


async def _fallback_area(
    client: DiscoverSwissClient, locality: str | None, lang: str
) -> str | None:
    """An area id for ``locality``, if one can be had without `/search`.

    ``resolve_area`` goes through `/search`, which is exactly what is refused;
    it only answers here from the cache. ``None`` is not an error — the scan
    then covers the whole collection and the locality is matched client-side.
    """
    if not locality:
        return None
    try:
        lookup = await client.resolve_area(locality, lang=lang)
    except SearchUnavailableError:
        return None
    return lookup.identifier


async def _scan_lists(
    client: DiscoverSwissClient,
    endpoints: tuple[str, ...],
    *,
    area_id: str | None,
    near: GeoPoint | None,
    radius_km: float,
    locality: str | None,
    types: list[str] | None,
    lang: str,
) -> _FallbackScan:
    """Read the collections page by page, then cut by type, locality and distance."""
    rows: list[dict[str, Any]] = []
    total: int | None = None
    calls = 0
    skipped: list[str] = []
    for endpoint in endpoints:
        if calls >= FALLBACK_MAX_CALLS:
            skipped.append(endpoint)
            continue
        token: str | None = None
        while True:
            page = await client.list_fallback(
                endpoint, contained_in_place=area_id, top=FALLBACK_TOP, token=token, lang=lang
            )
            calls += 1
            if token is None and page.total is not None:
                total = (total or 0) + page.total
            rows.extend(page.data)
            token = page.next_token
            if not token:
                break
            if calls >= FALLBACK_MAX_CALLS:
                # Part of this collection is unread: the scan is incomplete
                # even though the endpoint itself is not skipped.
                skipped.append(f"{endpoint} (partly)")
                break

    matched = rows
    if types:
        wanted = set(types)
        matched = [row for row in matched if _leaf_types(row) & wanted]
    if locality:
        target = locality.strip().casefold()
        matched = [
            row
            for row in matched
            if isinstance(row.get("address"), dict)
            and str(row["address"].get("addressLocality") or "").strip().casefold() == target
        ]
    if near is not None:
        matched = filter_by_distance(matched, near.lat, near.lon, radius_km)
    return _FallbackScan(
        matched=matched,
        scanned=len(rows),
        collection_total=total,
        complete=not skipped,
        skipped_endpoints=skipped,
        retrieved_at=_now(),
    )


def _fallback_applied(
    scan: _FallbackScan,
    endpoints: tuple[str, ...],
    area_id: str | None,
    near: GeoPoint | None,
    radius_km: float,
    locality: str | None,
    types: list[str] | None,
) -> dict[str, Any]:
    return {
        "mode": "list_fallback",
        "endpoints": list(endpoints),
        "containedInPlace": area_id,
        "near": near.model_dump() if near else None,
        "radius_km": radius_km if near else None,
        "locality": locality,
        "types": types,
        "rows_scanned": scan.scanned,
        "collection_total": scan.collection_total,
        "scan_complete": scan.complete,
    }


def _fallback_hint(
    scan: _FallbackScan, ignored: str | None, returned: int, page_hint: str | None
) -> str:
    parts = [FALLBACK_HINT]
    if ignored:
        parts.append(ignored)
    if not scan.complete:
        parts.append(
            f"The call budget ran out after {scan.scanned} of {scan.collection_total} listed "
            f"rows; not read: {', '.join(scan.skipped_endpoints)}. Results may be incomplete — "
            "do not conclude that something is absent."
        )
    if returned == 0 and page_hint:
        parts.append(page_hint)
    return " ".join(parts)


def _slice(rows: list[dict[str, Any]], page: int, page_size: int) -> list[dict[str, Any]]:
    start = (page - 1) * page_size
    return rows[start : start + page_size]


async def _search_fallback(client: DiscoverSwissClient, params: SearchInput) -> SearchResponse:
    project = client.settings.project
    ignored_parameters = ["query"] if params.query else []
    ignored = _ignored_text(ignored_parameters)
    if params.near is None and not params.locality:
        return SearchResponse(
            project=project,
            provenance="list_fallback",
            retrieved_at=_now(),
            source_freshness=None,
            degraded="search_unavailable",
            page=params.page,
            page_size=params.page_size,
            applied={"mode": "list_fallback", "endpoints": []},
            ignored_parameters=ignored_parameters,
            hint=" ".join(
                p
                for p in (
                    FALLBACK_HINT,
                    ignored,
                    "Without full text the lists need `near` or `locality` to bound the area; "
                    "nothing was fetched. Ask again with one of them.",
                )
                if p
            ),
        )

    endpoints = fallback_endpoints(params.types)
    radius = params.radius_km or FALLBACK_DEFAULT_RADIUS_KM
    try:
        area_id = await _fallback_area(client, params.locality, params.lang)
        scan = await _scan_lists(
            client,
            endpoints,
            area_id=area_id,
            near=params.near,
            radius_km=radius,
            locality=params.locality,
            types=params.types,
            lang=params.lang,
        )
    except DiscoverSwissError as exc:
        if exc.degraded is None:
            raise
        return SearchResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            **degraded_envelope_fields(exc),
        )

    window = _slice(scan.matched, params.page, params.page_size)
    screened = screen(window)
    kept = screened.kept
    excluded_default = 0
    if params.types is None:
        before = len(kept)
        kept = [obj for obj in kept if not is_default_excluded(obj)]
        excluded_default = before - len(kept)
    hits = [Hit(**_hit_fields(obj, params.near)) for obj in kept]
    page_hint = _paged_hint(
        len(scan.matched),
        len(window),
        len(hits),
        params.page,
        FALLBACK_EMPTY_HINT,
        by_license=screened.excluded_by_license,
        test_objects=screened.excluded_test_objects,
        default_types=excluded_default,
    )
    return SearchResponse(
        provenance="list_fallback",
        retrieved_at=scan.retrieved_at,
        source_freshness=_freshness(kept),
        project=project,
        degraded="search_unavailable",
        hint=_fallback_hint(scan, ignored, len(hits), page_hint),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        excluded_by_default_types=excluded_default,
        upstream_count=len(scan.matched),
        fetched=len(window),
        returned=len(hits),
        page=params.page,
        page_size=params.page_size,
        has_more=params.page * params.page_size < len(scan.matched),
        applied=_fallback_applied(
            scan, endpoints, area_id, params.near, radius, params.locality, params.types
        ),
        ignored_parameters=ignored_parameters,
        hits=hits,
    )


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
    if isinstance(result, SearchUnavailableError):
        return await _search_fallback(client, params)
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
    hint = _paged_hint(
        upstream_count,
        fetched,
        len(hits),
        params.page,
        SEARCH_EMPTY_HINT,
        by_license=screened.excluded_by_license,
        test_objects=screened.excluded_test_objects,
        default_types=excluded_default,
    )
    syntax_note = query_syntax_note(params.query) if fetched == 0 else None
    if syntax_note:
        hint = f"{syntax_note} {hint}" if hint else syntax_note
    return SearchResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        source_freshness=_freshness(kept),
        project=project,
        hint=hint,
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
    except InvalidIdentifierError:
        # The identifier failed the client's shape gate: nothing was sent, and
        # to the model this is the same situation as a 404. Only this case —
        # a 4xx from discover.swiss itself is not «unknown identifier» and
        # reaches the caller as an error (audit FID-003).
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

    if is_test_object(obj):
        # «Demo Event» at «Strasse 1, PLZ Ort» is withheld by every list tool;
        # a detail call by identifier must not be the way round it (FID-L03).
        return DetailResponse(
            identifier=identifier,
            name=name,
            license=licence,
            attribution=credit,
            project=project,
            provenance=provenance,
            retrieved_at=retrieved_at,
            source_freshness=last_modified,
            excluded_test_objects=1,
            hint=TEST_OBJECT_HINT,
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
    if isinstance(result, SearchUnavailableError):
        return await _accommodation_fallback(client, params)
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


def _ignored_accommodation_filters(params: FindAccommodationInput) -> list[str]:
    """The filters a list row cannot answer: the list ``select`` has no star rating,
    price band, amenities or accessibility partner."""
    return [
        name
        for name, active in (
            ("stars_min", params.stars_min is not None),
            ("garni", params.garni is not None),
            ("price_range", params.price_range is not None),
            ("amenities", bool(params.amenities)),
            ("accessible", params.accessible),
        )
        if active
    ]


def _ignored_text(ignored: list[str]) -> str | None:
    if not ignored:
        return None
    return (
        f"Ignored in this mode: {', '.join(ignored)} — the lists do not carry them, so the "
        "hits below are NOT filtered by them and are wider than asked for; check each with "
        "`get_details`."
    )


async def _accommodation_fallback(
    client: DiscoverSwissClient, params: FindAccommodationInput
) -> AccommodationResponse:
    project = client.settings.project
    ignored = _ignored_accommodation_filters(params)
    endpoints: tuple[str, ...] = ("lodgingbusinesses",)
    radius = params.radius_km or FALLBACK_DEFAULT_RADIUS_KM
    try:
        area_id = await _fallback_area(client, params.locality, params.lang)
        scan = await _scan_lists(
            client,
            endpoints,
            area_id=area_id,
            near=params.near,
            radius_km=radius,
            locality=params.locality,
            types=None,
            lang=params.lang,
        )
    except DiscoverSwissError as exc:
        if exc.degraded is None:
            raise
        return AccommodationResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            **degraded_envelope_fields(exc),
        )

    window = _slice(scan.matched, params.page, params.page_size)
    screened = screen(window)
    hits = [_accommodation_hit(obj, params.near) for obj in screened.kept]
    freshness = _freshness(screened.kept)
    page_hint = _paged_hint(
        len(scan.matched),
        len(window),
        len(hits),
        params.page,
        FALLBACK_EMPTY_HINT,
        by_license=screened.excluded_by_license,
        test_objects=screened.excluded_test_objects,
    )
    return AccommodationResponse(
        provenance="list_fallback",
        retrieved_at=scan.retrieved_at,
        source_freshness=freshness,
        project=project,
        degraded="search_unavailable",
        disclaimer=(
            disclaimer_b([h.attribution.provider for h in hits], freshness, params.lang)
            if hits
            else None
        ),
        hint=_fallback_hint(scan, _ignored_text(ignored), len(hits), page_hint),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        upstream_count=len(scan.matched),
        fetched=len(window),
        returned=len(hits),
        page=params.page,
        page_size=params.page_size,
        has_more=params.page * params.page_size < len(scan.matched),
        applied=_fallback_applied(
            scan, endpoints, area_id, params.near, radius, params.locality, None
        ),
        ignored_parameters=ignored,
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
        **TOUR_KINDS.get(params.kind, {}),
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


# ---------------------------------------------------------------------------
# Shared by tools 5–7: region lookup
# ---------------------------------------------------------------------------


def _unresolved_area_hint(lookup: AreaLookup, what: str) -> str:
    """The hint for a region name that matched no area: never an unfiltered search."""
    return (
        f"{lookup.hint} Pass one of these names as `region`, or use `near` with a coordinate "
        f"instead. No {what} was run."
    )


# ---------------------------------------------------------------------------
# Tool 5 — find_events
# ---------------------------------------------------------------------------

EVENTS_EMPTY_HINT = (
    "No open-licensed event in range. This source holds only about 20 events, so an empty "
    "answer says little about what is on. Widen the date range; then point the user to the "
    "regional calendar (e.g. zuerich.com/events for Zurich) — do not guess events."
)

# The index writes 2099-12-31T23:59:59 into `nextOccurrence` for an event
# without a concrete date (Schweizer Genusswoche, f4_odata.json). Any year from
# here on is read as «no date», never as a date.
SENTINEL_YEAR = 2099

# What `date_note` says when no concrete date exists.
DATE_OPEN_NOTE: dict[str, str] = {
    "de": "Termin offen",
    "fr": "Date à confirmer",
    "it": "Data da definire",
    "en": "Date to be announced",
}

# The default range: the next 30 days, as the brief sets it.
EVENTS_DEFAULT_DAYS = 30
EVENTS_MAX_RANGE_DAYS = 366

EVENT_SELECT_FIELDS: tuple[str, ...] = (
    "identifier",
    "name",
    "type",
    "additionalType",
    "address",
    "geo",
    "dataGovernance",
    "lastModified",
    "link",
    "nextOccurrence",
    "schedule",
    "organizer",
)
EVENT_SELECT = ",".join(EVENT_SELECT_FIELDS)
assert set(EVENT_SELECT_FIELDS) <= set(SEARCH_SELECT_FIELDS)

ZURICH = ZoneInfo("Europe/Zurich")


def _today() -> date:
    """Today in Switzerland — not in UTC, where it is still yesterday until 02:00."""
    return datetime.now(ZURICH).date()


class FindEventsInput(_PagedInput):
    """Events in a date range, optionally bounded by place."""

    near: GeoPoint | None = Field(default=None, description="Rank by distance from this point.")
    radius_km: float | None = Field(
        default=None, gt=0, le=200, description="Only with `near`: cut-off radius in km."
    )
    locality: str | None = Field(
        default=None,
        max_length=100,
        description="Exact municipality name from the address (e.g. 'St.Gallen'). No fuzzy match.",
    )
    region: str | None = Field(
        default=None,
        max_length=100,
        description="Area name, exact (e.g. 'Appenzellerland'); resolved to an area id.",
    )
    # A factory, not a value: a literal default would be the day the schema
    # was built, and the tool hash would change every midnight.
    from_date: date = Field(
        default_factory=_today,
        description="First day of the range, YYYY-MM-DD. Default: today (Europe/Zurich).",
    )
    to_date: date | None = Field(
        default=None,
        description=f"Last day of the range, inclusive. Default: from_date + {EVENTS_DEFAULT_DAYS} days.",
    )

    @model_validator(mode="after")
    def _check(self) -> FindEventsInput:
        _check_radius(self.near, self.radius_km)
        end = self.effective_to_date
        if end < self.from_date:
            raise ValueError("`to_date` lies before `from_date`.")
        if (end - self.from_date).days > EVENTS_MAX_RANGE_DAYS:
            raise ValueError(f"The date range is limited to {EVENTS_MAX_RANGE_DAYS} days.")
        return self

    @property
    def effective_to_date(self) -> date:
        return self.to_date or self.from_date + timedelta(days=EVENTS_DEFAULT_DAYS)


class EventHit(BaseModel):
    identifier: str
    name: str | None = None
    # ISO timestamp of the next date, or None when there is none — the 2099
    # sentinel included. Never a date in 2099.
    next_occurrence: str | None = None
    # True when the provider gives no concrete date; `date_note` then says so
    # in the requested language («Termin offen»).
    date_open: bool = False
    date_note: str | None = None
    # The schedule entry that overlaps the requested range (date, plus time
    # where the provider gives one).
    start: str | None = None
    end: str | None = None
    locality: str | None = None
    distance_km: float | None = None
    organizer_name: str | None = None
    website: str | None = None
    attribution: Attribution


class EventsResponse(_PagedResponse):
    area: AreaInfo | None = None
    hits: list[EventHit] = Field(default_factory=list)


def event_date_filter(from_date: date, to_date: date) -> str:
    """OData overlap filter on the schedule, verified live (PROBE_VERIFY 4).

    Not ``scheduleStart``/``scheduleEnd``: those apply after the search, so
    ``count`` and paging stop being reliable (the filtering how-to says so,
    and the probe got 7 hits where the OData form counts 18).
    """
    return (
        f"schedule/any(item: item/endDate ge {from_date.isoformat()}T00:00:00Z "
        f"and item/startDate le {to_date.isoformat()}T23:59:59Z)"
    )


def build_events_body(params: FindEventsInput, area_id: str | None) -> dict[str, Any]:
    conditions = [event_date_filter(params.from_date, params.effective_to_date)]
    if params.near is not None and params.radius_km is not None:
        conditions.append(geo_distance_filter(params.near, params.radius_km))
    body: dict[str, Any] = {
        "type": ["Event"],
        "containedInPlace": [area_id] if area_id else None,
        "addressLocality": [params.locality] if params.locality else None,
        "scoringReferencePoint": scoring_point(params.near) if params.near else None,
        # One string joined with `and` — the combined form verified on tours.
        "filters": [" and ".join(conditions)],
        "resultsPerPage": params.page_size,
        "currentPage": params.page,
        "select": EVENT_SELECT,
    }
    return {k: v for k, v in body.items() if v is not None}


def _is_sentinel(stamp: str | None) -> bool:
    if not stamp or len(stamp) < 4 or not stamp[:4].isdigit():
        return False
    return int(stamp[:4]) >= SENTINEL_YEAR


def _moment(day: Any, clock: Any) -> str | None:
    """``YYYY-MM-DD`` plus ``THH:MM[:SS]`` where a time is given; None for the sentinel."""
    if not isinstance(day, str) or len(day) < 10:
        return None
    stamp = day[:10]
    if isinstance(clock, str) and clock.strip():
        stamp = f"{stamp}T{clock.strip()}"
    return None if _is_sentinel(stamp) else stamp


def _schedule_entry(obj: dict[str, Any], from_date: date) -> dict[str, Any] | None:
    """The first schedule entry still running on ``from_date``, else the first one."""
    entries = [e for e in obj.get("schedule") or [] if isinstance(e, dict)]
    if not entries:
        return None
    first_day = from_date.isoformat()
    for entry in entries:
        end = entry.get("endDate") or entry.get("startDate")
        if isinstance(end, str) and end[:10] >= first_day:
            return entry
    return entries[0]


def _event_hit(obj: dict[str, Any], params: FindEventsInput) -> EventHit:
    fields = _hit_fields(obj, params.near)
    entry = _schedule_entry(obj, params.from_date) or {}
    start = _moment(entry.get("startDate"), entry.get("startTime"))
    end = _moment(entry.get("endDate"), entry.get("endTime"))

    raw_next = _str_or_none(obj.get("nextOccurrence"))
    if raw_next is not None and _is_sentinel(raw_next):
        next_occurrence = None
    else:
        # `nextOccurrence` is missing on some hits (probe: None for two of
        # three); the schedule is the fallback.
        next_occurrence = raw_next or start

    organizer = obj.get("organizer") if isinstance(obj.get("organizer"), dict) else {}
    date_open = next_occurrence is None
    return EventHit(
        identifier=fields["identifier"],
        name=fields["name"],
        next_occurrence=next_occurrence,
        date_open=date_open,
        date_note=DATE_OPEN_NOTE.get(params.lang, DATE_OPEN_NOTE["en"]) if date_open else None,
        start=start,
        end=end,
        locality=fields["locality"],
        distance_km=fields["distance_km"],
        organizer_name=_str_or_none(organizer.get("name")),
        website=fields["website"],
        attribution=fields["attribution"],
    )


async def find_events_impl(client: DiscoverSwissClient, params: FindEventsInput) -> EventsResponse:
    project = client.settings.project
    area: AreaInfo | None = None
    area_id: str | None = None

    if params.region:
        try:
            lookup = await client.resolve_area(params.region, lang=params.lang)
        except DiscoverSwissError as exc:
            if exc.degraded is None:
                raise
            return EventsResponse(
                project=project,
                page=params.page,
                page_size=params.page_size,
                **degraded_envelope_fields(exc),
            )
        area = _area_info(lookup)
        if lookup.identifier is None:
            return EventsResponse(
                project=project,
                provenance=lookup.provenance,
                retrieved_at=lookup.retrieved_at,
                source_freshness=None,
                page=params.page,
                page_size=params.page_size,
                area=area,
                hint=_unresolved_area_hint(lookup, "event search"),
            )
        area_id = lookup.identifier

    body = build_events_body(params, area_id)
    applied = {k: v for k, v in body.items() if k != "select"}

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return EventsResponse(
            project=project,
            page=params.page,
            page_size=params.page_size,
            applied=applied,
            area=area,
            **degraded_envelope_fields(result),
        )

    # Both gates are mandatory here: «Demo Event» is live in the index, and
    # Guidle events are all-rights-reserved.
    screened = screen(result.values)
    hits = [_event_hit(obj, params) for obj in screened.kept]
    fetched = len(result.values)
    upstream_count, has_more = _paging(result, params.page, params.page_size, fetched)
    freshness = _freshness(screened.kept)
    return EventsResponse(
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
            EVENTS_EMPTY_HINT,
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


# ---------------------------------------------------------------------------
# Tool 6 — webcams_near
# ---------------------------------------------------------------------------

WEBCAM_PAGE_SIZE = 20
WEBCAM_DEFAULT_RADIUS_KM = 25.0

# `link[].type` values that point at the provider's live image
# (Webcam Atzmännig: `WebDetail` → sky-cam.ch/…/livebild.php).
LIVE_LINK_TYPES = frozenset({"WebDetail", "WebLink"})

SNAPSHOT_NOTE = "last stored snapshot, not live — may be hours old"

WEBCAM_SELECT_FIELDS: tuple[str, ...] = (
    "identifier",
    "name",
    "type",
    "additionalType",
    "address",
    "geo",
    "dataGovernance",
    "lastModified",
    "link",
    "image",
)
WEBCAM_SELECT = ",".join(WEBCAM_SELECT_FIELDS)
assert set(WEBCAM_SELECT_FIELDS) <= set(SEARCH_SELECT_FIELDS)


def _webcams_empty_hint(radius_km: float | None) -> str:
    scope = f"within {radius_km:g} km" if radius_km is not None else "in this area"
    return (
        f"No webcam {scope}. All webcams in this source are in Eastern Switzerland (St. Gallen, "
        "Thurgau, Toggenburg, Heidiland, Glarnerland, Appenzell). If the point lies near that "
        "region, widen `radius_km`; otherwise tell the user this source has no webcam there — "
        "do not invent one."
    )


class WebcamsNearInput(BaseModel):
    """Webcams around a point or in a region."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    near: GeoPoint | None = Field(
        default=None, description="Point to search around. `near` or `region` is required."
    )
    region: str | None = Field(
        default=None,
        max_length=100,
        description="Area name, exact (e.g. 'Toggenburg'); resolved to an area id.",
    )
    radius_km: float = Field(
        default=WEBCAM_DEFAULT_RADIUS_KM,
        gt=0,
        le=200,
        description="Only with `near`: hard cut-off radius in km. Default 25.",
    )
    page: int = Field(default=1, ge=1, le=100, description="1-based page of 20 webcams.")
    lang: Lang = Field(default="de", description="Language of names (de, fr, it, en).")

    @model_validator(mode="after")
    def _place_required(self) -> WebcamsNearInput:
        if self.near is None and not self.region:
            raise ValueError("Give `near` or `region`: webcams are always looked up by place.")
        return self


class WebcamHit(BaseModel):
    identifier: str
    name: str | None = None
    locality: str | None = None
    distance_km: float | None = None
    # The provider's live image page.
    live_url: str | None = None
    # A stored still on media-v2.discover.swiss — not live.
    snapshot_url: str | None = None
    snapshot_note: str | None = None
    attribution: Attribution


class WebcamsResponse(_PagedResponse):
    area: AreaInfo | None = None
    hits: list[WebcamHit] = Field(default_factory=list)


def build_webcams_body(params: WebcamsNearInput, area_id: str | None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "type": ["Webcam"],
        "containedInPlace": [area_id] if area_id else None,
        "filters": (
            [geo_distance_filter(params.near, params.radius_km)]
            if params.near is not None
            else None
        ),
        "scoringReferencePoint": scoring_point(params.near) if params.near else None,
        "resultsPerPage": WEBCAM_PAGE_SIZE,
        "currentPage": params.page,
        "select": WEBCAM_SELECT,
    }
    return {k: v for k, v in body.items() if v is not None}


def _live_url(obj: dict[str, Any]) -> str | None:
    links = obj.get("link")
    if not isinstance(links, list):
        return None
    for link in links:
        if isinstance(link, dict) and link.get("type") in LIVE_LINK_TYPES:
            url = _str_or_none(link.get("url"))
            if url:
                return url
    return None


def _webcam_hit(obj: dict[str, Any], near: GeoPoint | None) -> WebcamHit:
    fields = _hit_fields(obj, near)
    snapshot = _image_url(obj)
    return WebcamHit(
        identifier=fields["identifier"],
        name=fields["name"],
        locality=fields["locality"],
        distance_km=fields["distance_km"],
        live_url=_live_url(obj),
        snapshot_url=snapshot,
        snapshot_note=SNAPSHOT_NOTE if snapshot else None,
        attribution=fields["attribution"],
    )


async def webcams_near_impl(
    client: DiscoverSwissClient, params: WebcamsNearInput
) -> WebcamsResponse:
    project = client.settings.project
    area: AreaInfo | None = None
    area_id: str | None = None

    if params.region:
        try:
            lookup = await client.resolve_area(params.region, lang=params.lang)
        except DiscoverSwissError as exc:
            if exc.degraded is None:
                raise
            return WebcamsResponse(
                project=project,
                page=params.page,
                page_size=WEBCAM_PAGE_SIZE,
                **degraded_envelope_fields(exc),
            )
        area = _area_info(lookup)
        if lookup.identifier is None:
            return WebcamsResponse(
                project=project,
                provenance=lookup.provenance,
                retrieved_at=lookup.retrieved_at,
                source_freshness=None,
                page=params.page,
                page_size=WEBCAM_PAGE_SIZE,
                area=area,
                hint=_unresolved_area_hint(lookup, "webcam search"),
            )
        area_id = lookup.identifier

    body = build_webcams_body(params, area_id)
    applied = {k: v for k, v in body.items() if k != "select"}

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return WebcamsResponse(
            project=project,
            page=params.page,
            page_size=WEBCAM_PAGE_SIZE,
            applied=applied,
            area=area,
            **degraded_envelope_fields(result),
        )

    screened = screen(result.values)
    hits = [_webcam_hit(obj, params.near) for obj in screened.kept]
    fetched = len(result.values)
    upstream_count, has_more = _paging(result, params.page, WEBCAM_PAGE_SIZE, fetched)
    return WebcamsResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        source_freshness=_freshness(screened.kept),
        project=project,
        hint=_paged_hint(
            upstream_count,
            fetched,
            len(hits),
            params.page,
            _webcams_empty_hint(params.radius_km if params.near else None),
            by_license=screened.excluded_by_license,
            test_objects=screened.excluded_test_objects,
        ),
        excluded_by_license=screened.excluded_by_license,
        excluded_test_objects=screened.excluded_test_objects,
        upstream_count=upstream_count,
        fetched=fetched,
        returned=len(hits),
        page=params.page,
        page_size=WEBCAM_PAGE_SIZE,
        has_more=has_more,
        applied=applied,
        area=area,
        hits=hits,
    )


# ---------------------------------------------------------------------------
# Tool 7 — explore_area
# ---------------------------------------------------------------------------

DEFAULT_EXPLORE_FACETS: tuple[str, ...] = ("leafType", "sourcePartner", "season", "priceRange")

# Values per facet. Twenty keeps `containedInPlace/id` useful as an area
# index while a response stays a few kilobytes.
EXPLORE_FACET_VALUES = 20
EXPLORE_DEFAULT_RADIUS_KM = 10.0

UNKNOWN_FACETS_HINT = (
    "Facet(s) {names} are not valid names and were not sent — the upstream API rejects the "
    "whole request for an unknown facet; valid names are leafType, containedInPlace/id, "
    "rating/difficulty, sourcePartner, season, priceRange, address/addressLocality, "
    "categoryTree."
)

MISSING_FACETS_HINT = (
    "Facet(s) {names} were silently dropped by the upstream API — the name is probably wrong; "
    "valid names are leafType, containedInPlace/id, rating/difficulty, sourcePartner, season, "
    "priceRange, address/addressLocality, categoryTree."
)

EXPLORE_EMPTY_HINT = (
    "Nothing in this scope. Check `locality` against the address spelling or widen "
    "`radius_km`. Points of interest are covered for Zurich, Eastern Switzerland, "
    "Liechtenstein and Engadin; hotels nationwide."
)

# The eight names are verified; the tool must agree with the client on them.
assert set(VERIFIED_FACETS) == {
    "leafType",
    "containedInPlace/id",
    "rating/difficulty",
    "sourcePartner",
    "season",
    "priceRange",
    "address/addressLocality",
    "categoryTree",
}


class ExploreAreaInput(BaseModel):
    """Facet counts for a scope — what exists before anything is searched."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    region: str | None = Field(
        default=None,
        max_length=100,
        description="Area name, exact (e.g. 'Glarnerland'); resolved to an area id.",
    )
    locality: str | None = Field(
        default=None, max_length=100, description="Exact municipality name from the address."
    )
    near: GeoPoint | None = Field(default=None, description="Centre of a radius scope.")
    radius_km: float | None = Field(
        default=None,
        gt=0,
        le=200,
        description=f"Only with `near`: radius in km. Default {EXPLORE_DEFAULT_RADIUS_KM:g}.",
    )
    facets: list[str] = Field(
        default=list(DEFAULT_EXPLORE_FACETS),
        min_length=1,
        max_length=12,
        description=(
            "Facet names (OData spelling): leafType, containedInPlace/id, rating/difficulty, "
            "sourcePartner, season, priceRange, address/addressLocality, categoryTree. The "
            "short forms containedInPlace, ratingDifficulty and addressLocality are mapped; "
            "any other name is not sent and is reported in missing_facets."
        ),
    )
    lang: Lang = Field(default="de", description="Language of facet labels (de, fr, it, en).")

    @model_validator(mode="after")
    def _radius_needs_near(self) -> ExploreAreaInput:
        _check_radius(self.near, self.radius_km)
        return self


class FacetValue(BaseModel):
    value: str
    label: str | None = None
    count: int | None = None


class ExploreAreaResponse(Envelope):
    # Upstream count for the scope, before the licence gate.
    total: int | None = None
    facets: dict[str, list[FacetValue]] = Field(default_factory=dict)
    # The names sent upstream, after mapping short forms.
    requested_facets: list[str] = Field(default_factory=list)
    # Asked for and not in the answer: names this server does not send (unknown
    # upstream answers 400), and sent names the upstream API dropped quietly.
    missing_facets: list[str] = Field(default_factory=list)
    area: AreaInfo | None = None
    applied: dict[str, Any] = Field(default_factory=dict)


def build_explore_body(
    params: ExploreAreaInput, area_id: str | None, facet_names: list[str]
) -> dict[str, Any]:
    radius = params.radius_km or EXPLORE_DEFAULT_RADIUS_KM
    body: dict[str, Any] = {
        "containedInPlace": [area_id] if area_id else None,
        "addressLocality": [params.locality] if params.locality else None,
        "filters": [geo_distance_filter(params.near, radius)] if params.near is not None else None,
        "resultsPerPage": 1,
        "select": "identifier",
        "facets": (
            [facet_request(name, EXPLORE_FACET_VALUES) for name in facet_names]
            if facet_names
            else None
        ),
    }
    return {k: v for k, v in body.items() if v is not None}


def _facet_list(facets: dict[str, Any], name: str) -> list[FacetValue]:
    values: list[FacetValue] = []
    for raw in facet_values(facets, name):
        value = raw.get("value")
        if value is None:
            continue
        label = raw.get("name")
        count = raw.get("count")
        values.append(
            FacetValue(
                value=str(value),
                label=str(label) if label is not None else None,
                count=count if isinstance(count, int) and not isinstance(count, bool) else None,
            )
        )
    return values


async def explore_area_impl(
    client: DiscoverSwissClient, params: ExploreAreaInput
) -> ExploreAreaResponse:
    project = client.settings.project
    facet_names, unknown = partition_facet_names(params.facets)
    area: AreaInfo | None = None
    area_id: str | None = None

    if params.region:
        try:
            lookup = await client.resolve_area(params.region, lang=params.lang)
        except DiscoverSwissError as exc:
            if exc.degraded is None:
                raise
            return ExploreAreaResponse(
                project=project,
                requested_facets=facet_names,
                missing_facets=unknown,
                **degraded_envelope_fields(exc),
            )
        area = _area_info(lookup)
        if lookup.identifier is None:
            return ExploreAreaResponse(
                project=project,
                provenance=lookup.provenance,
                retrieved_at=lookup.retrieved_at,
                source_freshness=None,
                requested_facets=facet_names,
                missing_facets=unknown,
                area=area,
                hint=_unresolved_area_hint(lookup, "facet count"),
            )
        area_id = lookup.identifier

    body = build_explore_body(params, area_id, facet_names)
    applied = {k: v for k, v in body.items() if k not in ("select", "facets")}

    result = await _run_search(client, body, params.lang)
    if isinstance(result, DiscoverSwissError):
        return ExploreAreaResponse(
            project=project,
            requested_facets=facet_names,
            missing_facets=unknown,
            area=area,
            applied=applied,
            **degraded_envelope_fields(result),
        )

    facets = {
        name: _facet_list(result.facets, name)
        for name in facet_names
        if name in result.facets and name not in result.missing_facets
    }
    hints: list[str] = []
    if unknown:
        hints.append(UNKNOWN_FACETS_HINT.format(names=", ".join(unknown)))
    if result.missing_facets:
        hints.append(MISSING_FACETS_HINT.format(names=", ".join(result.missing_facets)))
    if result.count == 0:
        hints.append(EXPLORE_EMPTY_HINT)
    return ExploreAreaResponse(
        provenance=result.provenance,
        retrieved_at=result.retrieved_at,
        # Facet counts are an aggregate over the scope, not one object with a
        # modification date.
        source_freshness=None,
        project=project,
        total=result.count,
        facets=facets,
        requested_facets=facet_names,
        missing_facets=unknown + list(result.missing_facets),
        area=area,
        applied=applied,
        hint=" ".join(hints) if hints else None,
    )


# ---------------------------------------------------------------------------
# Tool 8 — source_status
# ---------------------------------------------------------------------------

COVERAGE_NOTE = (
    "Hotels and other lodging nationwide (5'275). Points of interest, tours and webcams for "
    "Zurich, Eastern Switzerland, Liechtenstein and Engadin Scuol. Events thin (about 20). "
    "No points of interest for the Bernese Oberland, Central Switzerland, Valais, Ticino or "
    "the Romandie."
)

ENTITLEMENT_NOTE = (
    "Search access on the Infocenter Open product is used as observed live; written "
    "confirmation from discover.swiss: {state}"
)

STATUS_HINTS: dict[str, str] = {
    "no_key": (
        "DISCOVER_SWISS_KEY is not set; no call was made. Every other tool fails until it is."
    ),
    "quota_exhausted": DEGRADED_HINTS["quota_exhausted"],
    "rate_limited": DEGRADED_HINTS["rate_limited"],
    "upstream_unreachable": (
        "discover.swiss did not answer its status endpoint. Results from other tools are not "
        "evidence about the data until it does."
    ),
    "search_unavailable": (
        "discover.swiss refuses its search endpoint. `search` and `find_accommodation` answer "
        "from typed lists (provenance list_fallback, no full text); find_tours, find_events, "
        "webcams_near and explore_area answer degraded. Search is tried again after 10 minutes."
    ),
}


class SourceStatusResponse(Envelope):
    api_key_configured: bool
    reachable: bool
    search_available: bool
    base_url: str
    calls_last_minute: int
    monthly_quota_exhausted_since: datetime | None = None
    last_success: datetime | None = None
    cache_entries: int = 0
    # Objects in the whole index, from an unfiltered explore_area (60 min cache).
    index_total: int | None = None
    coverage: str = COVERAGE_NOTE
    entitlement_note: str


def _entitlement_note(client: DiscoverSwissClient) -> str:
    confirmed = client.settings.entitlement_confirmed
    state = f"confirmed {confirmed.isoformat()}" if confirmed else "pending"
    return ENTITLEMENT_NOTE.format(state=state)


async def source_status_impl(client: DiscoverSwissClient) -> SourceStatusResponse:
    settings = client.settings
    key_set = bool(settings.api_key.get_secret_value())

    if not key_set:
        return SourceStatusResponse(
            provenance="live_api",
            retrieved_at=_now(),
            source_freshness=None,
            project=settings.project,
            api_key_configured=False,
            reachable=False,
            search_available=client.search_available,
            base_url=settings.base_url,
            calls_last_minute=0,
            entitlement_note=_entitlement_note(client),
            hint=STATUS_HINTS["no_key"],
        )

    state = await client.status()
    index_total: int | None = None
    if state["reachable"] and state["search_available"]:
        explored = await explore_area_impl(client, ExploreAreaInput(facets=["leafType"]))
        index_total = explored.total

    # Re-read after the explore call: a refused `/search` flips it.
    search_available = client.search_available
    degraded: str | None = None
    if state["quota_exhausted_since"] is not None:
        degraded = "quota_exhausted"
    elif state.get("rate_limited_for") is not None:
        degraded = "rate_limited"
    elif not state["reachable"]:
        degraded = "upstream_unreachable"
    elif not search_available:
        degraded = "search_unavailable"

    return SourceStatusResponse(
        provenance="live_api",
        retrieved_at=_now(),
        source_freshness=None,
        project=state["project"],
        degraded=degraded,
        hint=(
            STATUS_HINTS.get(degraded, "").format(
                seconds=f"{state.get('rate_limited_for') or 0:.0f}"
            )
            or None
            if degraded
            else None
        ),
        api_key_configured=True,
        reachable=state["reachable"],
        search_available=search_available,
        base_url=state["base_url"],
        calls_last_minute=client.calls_last_minute,
        monthly_quota_exhausted_since=state["quota_exhausted_since"],
        last_success=client.last_success,
        cache_entries=client.cache.live_entries(),
        index_total=index_total,
        entitlement_note=_entitlement_note(client),
    )
