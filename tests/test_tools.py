"""The four P2 tools, driven through their ``*_impl`` functions — offline, via respx.

**What the fixtures are, and what they are not.** The recorded search answers
(`probes/probe_out/search_dsod-content_1.json`, Landesmuseum, and
`search_dsod-content_4.json`, hotels around Interlaken) were taken with a
narrow ``select`` — identifier, name, type, address. A hit built from them
alone carries no ``dataGovernance``, so the licence gate would withhold all of
them, correctly. The builders below therefore add, per hit, the fields the tool
``select`` asks for, taken from the recorded detail objects of the *same*
objects where they exist (Landesmuseum, Hotel Du Nord: governance, geo,
lastModified). For every other hit the governance is constructed in the
recorded shape and marked as such. Identifiers and names stay the recorded
ones.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import httpx
import pytest
from conftest import json_response, probe_fixture
from pydantic import ValidationError

from discover_swiss_mcp.client import SEARCH_SELECT_FIELDS
from discover_swiss_mcp.tools import (
    ACCOMMODATION_EMPTY_HINT,
    REMOVED_HINT,
    SEARCH_EMPTY_HINT,
    TOOL_SELECT_FIELDS,
    TOURS_EMPTY_HINT,
    UNKNOWN_IDENTIFIER_HINT,
    FindAccommodationInput,
    FindToursInput,
    GeoPoint,
    GetDetailsInput,
    SearchInput,
    find_accommodation_impl,
    find_tours_impl,
    get_details_impl,
    search_impl,
)

INTERLAKEN = GeoPoint(lat=46.6863, lon=7.8632)

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _landesmuseum_detail() -> dict[str, Any]:
    return probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")


def _hotel_detail() -> dict[str, Any]:
    return probe_fixture("probe_detail_out", "detail_hotel_interlaken.json")


def _governance(acronym: str, name: str, licence: str) -> dict[str, Any]:
    """Constructed governance in the shape the probe recorded (one origin)."""
    partner = {
        "acronym": acronym,
        "identifier": acronym,
        "type": "schema.org/Partner",
        "name": name,
    }
    return {
        "origin": [{"datasource": acronym, "license": licence, "provider": partner}],
        "provider": partner,
        "source": partner,
    }


def landesmuseum_page() -> dict[str, Any]:
    """`search_dsod-content_1.json` (count 53) with governance added per hit."""
    recorded = probe_fixture("probe_out", "search_dsod-content_1.json")
    detail = _landesmuseum_detail()
    zht = _governance("zht", "Zürich Tourismus", "CC BY-SA")
    by_id = {
        "civ_px9-s28_bggg": {
            "dataGovernance": detail["dataGovernance"],
            "geo": detail["geo"],
            "lastModified": detail["lastModified"],
            "link": detail["link"],
            "disambiguatingDescription": "<p>Das Landesmuseum gleich beim Z&uuml;rcher HB.</p>",
        },
        "plc_s9t_qgsrctqd-ujqv-evjg-jquc-addqhtjsifeb": {
            "dataGovernance": _governance("ltm", "Liechtenstein Marketing", "CC BY-SA")
        },
        "loc_px9-s28_bbfiff": {"dataGovernance": zht},
        "civ_px9-s28_cdbcji": {"dataGovernance": zht},
        "log_x8-tdgf_bbajj": {"dataGovernance": _governance("hs", "HotellerieSuisse", "CC BY")},
    }
    values = [{**hit, **by_id[hit["identifier"]]} for hit in recorded["values"]]
    return {"count": recorded["count"], "values": values, "facets": {}}


def interlaken_page() -> dict[str, Any]:
    """`search_dsod-content_4.json` (hotels, count 3'093) with governance and stars."""
    recorded = probe_fixture("probe_out", "search_dsod-content_4.json")
    du_nord = _hotel_detail()
    hs = _governance("hs", "HotellerieSuisse", "CC BY")
    values = []
    for hit in recorded["values"]:
        hit = {**hit, "type": "LodgingBusiness", "additionalType": "Hotel"}
        if hit["identifier"] == du_nord["identifier"]:
            hit.update(
                dataGovernance=du_nord["dataGovernance"],
                geo=du_nord["geo"],
                starRating={
                    k: du_nord["starRating"][k] for k in ("ratingValue", "garni", "superior")
                },
                lastModified=du_nord["lastModified"],
                link=du_nord["link"],
            )
        else:
            hit["dataGovernance"] = hs
        values.append(hit)
    return {"count": recorded["count"], "values": values, "facets": {}}


def all_rights_reserved_event() -> dict[str, Any]:
    """A Guidle event as the probe found them: C-All-Rights-Reserved."""
    return {
        "identifier": "eve_gdl_arr",
        "name": "Konzert im Park",
        "type": "Event",
        "dataGovernance": _governance("gdl", "Guidle", "C-All-Rights-Reserved"),
    }


def demo_event() -> dict[str, Any]:
    """«Demo Event» with the placeholder address recorded in the production index."""
    return {
        "identifier": "eve_s9t_dshjrcer-tfsb-essd-rirq-hugidebuvjge",
        "name": "Demo Event",
        "type": "Event",
        "address": {
            "streetAddress": "Strasse 1",
            "postalCode": "PLZ",
            "addressLocality": "Ort",
            "email": "mail@example.ch",
        },
        "dataGovernance": _governance("ctd", "contentdesk", "CC BY-SA"),
    }


def hotel_room() -> dict[str, Any]:
    """The first recorded room row, in search-hit shape (no root licence)."""
    page = probe_fixture("probe_out", "raw_first_page_dsod-content_accommodations.json")
    row = copy.deepcopy(page["data"][0])
    row.pop("license", None)
    row.pop("containedInPlace", None)
    row["type"] = "Accommodation"
    return row


def meeting_room() -> dict[str, Any]:
    return {
        "identifier": "acc_meeting_1",
        "name": "Seminarraum Jungfrau",
        "type": "Accommodation",
        "additionalType": "MeetingRoom",
        "dataGovernance": _governance("hs", "HotellerieSuisse", "CC BY"),
    }


def _body(route) -> dict[str, Any]:
    return json.loads(route.calls.last.request.read())


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


def test_tool_select_stays_inside_the_verified_whitelist() -> None:
    """A field outside the 46 answers 400 for the whole call — `license` is the trap."""
    assert set(TOOL_SELECT_FIELDS) <= set(SEARCH_SELECT_FIELDS)
    assert "license" not in TOOL_SELECT_FIELDS


def test_page_size_is_capped_at_fifty() -> None:
    with pytest.raises(ValidationError):
        SearchInput(page_size=51)


# ---------------------------------------------------------------------------
# Tool 1 — search
# ---------------------------------------------------------------------------


async def test_search_happy_path_landesmuseum(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(landesmuseum_page()))
    result = await search_impl(client, SearchInput(query="Landesmuseum"))

    body = _body(route)
    assert body["project"] == ["dsod-content"]
    assert body["searchText"] == "Landesmuseum"
    assert body["resultsPerPage"] == 10 and body["currentPage"] == 1
    assert body["select"].split(",") == list(TOOL_SELECT_FIELDS)
    assert "searchFields" not in body  # match='all' is the index default: every field
    assert "leafType" not in body  # no types → not sent; the default is applied client-side

    assert result.upstream_count == 53
    assert result.fetched == 5 and result.returned == 5
    assert result.hint is None
    first = result.hits[0]
    assert first.identifier == "civ_px9-s28_bggg"
    assert first.name == "Landesmuseum Zürich"
    assert first.attribution.provider == "Zürich Tourismus"
    assert first.attribution.license == "CC BY-SA"
    assert first.website == "https://www.landesmuseum.ch"
    assert first.teaser == "Das Landesmuseum gleich beim Zürcher HB."
    assert all(hit.attribution.license != "unknown" for hit in result.hits)
    assert result.source_freshness == _landesmuseum_detail()["lastModified"]
    assert result.has_more is True


async def test_search_filters_and_counts_withheld_objects(api_mock, client) -> None:
    page = landesmuseum_page()
    page["values"] += [all_rights_reserved_event(), demo_event()]
    api_mock.post("/search").mock(return_value=json_response(page))

    result = await search_impl(client, SearchInput(query="Landesmuseum"))

    ids = {hit.identifier for hit in result.hits}
    assert "eve_gdl_arr" not in ids
    assert "eve_s9t_dshjrcer-tfsb-essd-rirq-hugidebuvjge" not in ids
    assert result.excluded_by_license == 1
    assert result.excluded_test_objects == 1
    assert result.upstream_count == 53
    assert result.fetched == 7
    assert result.returned == 5
    assert result.fetched == (
        result.returned
        + result.excluded_by_license
        + result.excluded_test_objects
        + result.excluded_by_default_types
    )


async def test_search_drops_rooms_by_default_and_counts_them(api_mock, client) -> None:
    page = landesmuseum_page()
    page["values"] += [hotel_room(), meeting_room()]
    route = api_mock.post("/search").mock(return_value=json_response(page))

    result = await search_impl(client, SearchInput(query="Zimmer"))

    assert "leafType" not in _body(route)
    assert result.excluded_by_default_types == 2
    assert all(hit.type != "Accommodation" for hit in result.hits)
    assert result.applied["default_type_exclusion"] is True


async def test_search_delivers_rooms_when_asked_for(api_mock, client) -> None:
    room = hotel_room()
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [room], "facets": {}})
    )

    result = await search_impl(client, SearchInput(query="Doppelzimmer", types=["HotelRoom"]))

    assert _body(route)["leafType"] == ["HotelRoom"]
    assert result.excluded_by_default_types == 0
    assert [hit.identifier for hit in result.hits] == [room["identifier"]]
    assert result.hits[0].leaf_type == "HotelRoom"
    assert result.hits[0].attribution.license == "CC BY-ND"


async def test_search_empty_result_carries_the_hint(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await search_impl(client, SearchInput(query="Xylophonmuseum", match="name"))

    assert result.returned == 0
    assert result.hint == SEARCH_EMPTY_HINT
    assert result.hint.strip()


async def test_search_page_of_only_withheld_hits_says_so(api_mock, client) -> None:
    """Not «nothing found»: something was found and withheld. Different advice."""
    api_mock.post("/search").mock(
        return_value=json_response(
            {"count": 12, "values": [all_rights_reserved_event()], "facets": {}}
        )
    )
    result = await search_impl(client, SearchInput(query="Konzert"))

    assert result.returned == 0
    assert result.hint and "withheld" in result.hint
    assert result.hint != SEARCH_EMPTY_HINT
    assert "1 not openly licensed" in result.hint
    # Room advice only when rooms were withheld: the live run of 2026-09-25
    # showed the generic wording sending a model after `types` for museums.
    assert "types" not in result.hint
    assert "Later pages may still hold servable hits" in result.hint


async def test_accommodation_page_of_only_withheld_hits_names_the_reason(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response(
            {"count": 1, "values": [all_rights_reserved_event()], "facets": {}}
        )
    )
    result = await find_accommodation_impl(client, FindAccommodationInput(locality="Interlaken"))
    assert result.hint == (
        "All 1 hits on this page were withheld: 1 not openly licensed "
        "(they may not be shown or described)."
    )


async def test_search_name_match_sends_search_fields(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    await search_impl(client, SearchInput(query="Landesmuseum", match="name"))
    assert _body(route)["searchFields"] == "name"


async def test_search_distance_hotel_du_nord_is_close_to_interlaken(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(interlaken_page()))

    result = await search_impl(
        client, SearchInput(types=["Hotel"], near=INTERLAKEN, radius_km=5, locality=None)
    )

    body = _body(route)
    # Longitude first: the spec's order, and the one a lat/lon habit gets wrong.
    assert body["scoringReferencePoint"] == "7.8632,46.6863"
    assert body["filters"] == ["geo.distance(geo, geography'POINT(7.8632 46.6863)') le 5.0"]
    du_nord = next(hit for hit in result.hits if hit.identifier == "log_x8-tdgf_bcfch")
    assert du_nord.distance_km is not None
    assert du_nord.distance_km < 2


async def test_search_near_without_radius_only_ranks(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(interlaken_page()))
    await search_impl(client, SearchInput(types=["Hotel"], near=INTERLAKEN))
    body = _body(route)
    assert "filters" not in body
    assert body["scoringReferencePoint"] == "7.8632,46.6863"


def test_search_radius_without_near_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchInput(query="Museum", radius_km=3)


async def test_search_locality_is_sent_as_exact_array(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    await search_impl(client, SearchInput(types=["Museum"], locality="Zürich"))
    assert _body(route)["addressLocality"] == ["Zürich"]


async def test_search_quota_is_a_degraded_state_not_an_error(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"message": "Out of call volume quota."}, status=403)
    )
    result = await search_impl(client, SearchInput(query="Rigi"))

    assert result.degraded == "quota_exhausted"
    assert result.hits == []
    assert result.hint and "quota" in result.hint


async def test_search_refused_is_search_unavailable(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    result = await search_impl(client, SearchInput(query="Rigi"))
    assert result.degraded == "search_unavailable"
    assert result.hint


# ---------------------------------------------------------------------------
# Tool 2 — get_details
# ---------------------------------------------------------------------------


async def test_details_happy_path_landesmuseum(api_mock, client) -> None:
    detail = _landesmuseum_detail()
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(return_value=json_response(detail))

    result = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))

    assert result.detail is not None
    assert result.detail["name"] == "Landesmuseum Zürich"
    assert "&uuml;" not in result.detail["description"]
    assert result.attribution is not None
    assert result.attribution.provider == "Zürich Tourismus"
    assert result.license == "CC BY-SA"
    assert result.no_derivatives is False
    assert result.removed is False
    assert result.hint is None
    assert result.disclaimer == (
        "Angaben von Zürich Tourismus via discover.swiss, Stand 03.09.2026. Öffnungszeiten "
        "und Preise ohne Gewähr — vor dem Besuch beim Anbieter prüfen."
    )
    assert len(json.dumps(result.detail, ensure_ascii=False).encode()) <= 8 * 1024


async def test_details_disclaimer_follows_lang(api_mock, client) -> None:
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response(_landesmuseum_detail())
    )
    result = await get_details_impl(
        client, GetDetailsInput(identifier="civ_px9-s28_bggg", lang="fr")
    )
    assert result.disclaimer and result.disclaimer.startswith("Informations de Zürich Tourismus")
    assert "03.09.2026" in result.disclaimer


async def test_details_second_call_reports_cached(api_mock, client) -> None:
    route = api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response(_landesmuseum_detail())
    )
    first = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    second = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    assert route.call_count == 1
    assert (first.provenance, second.provenance) == ("live_api", "cached")


async def test_details_unknown_identifier(api_mock, client) -> None:
    api_mock.get("/vertices/civ_does_not_exist").mock(return_value=httpx.Response(404))
    result = await get_details_impl(client, GetDetailsInput(identifier="civ_does_not_exist"))
    assert result.detail is None
    assert result.hint == UNKNOWN_IDENTIFIER_HINT


async def test_details_malformed_identifier_is_unknown_without_a_call(api_mock, client) -> None:
    route = api_mock.get(url__regex=r".*/vertices/.*").mock(return_value=httpx.Response(404))
    result = await get_details_impl(client, GetDetailsInput(identifier="../status"))
    assert route.call_count == 0
    assert result.hint == UNKNOWN_IDENTIFIER_HINT


async def test_details_removed_object_is_shown_and_flagged(api_mock, client) -> None:
    detail = {**_landesmuseum_detail(), "removed": True}
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(return_value=json_response(detail))
    result = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    assert result.removed is True
    assert result.detail is not None
    assert result.hint == REMOVED_HINT


async def test_details_closed_licence_withholds_content(api_mock, client) -> None:
    detail = {**_landesmuseum_detail(), "license": "C-All-Rights-Reserved"}
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(return_value=json_response(detail))
    result = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))

    assert result.detail is None
    assert result.excluded_by_license == 1
    assert result.name == "Landesmuseum Zürich"
    assert result.license == "C-All-Rights-Reserved"
    assert result.attribution is not None
    assert result.disclaimer is None


async def test_details_nd_licence_sets_no_derivatives(api_mock, client) -> None:
    detail = {**_hotel_detail(), "license": "CC BY-ND"}
    api_mock.get("/vertices/log_x8-tdgf_bcfch").mock(return_value=json_response(detail))
    result = await get_details_impl(client, GetDetailsInput(identifier="log_x8-tdgf_bcfch"))
    assert result.no_derivatives is True
    assert result.detail is not None


# ---------------------------------------------------------------------------
# Tool 3 — find_accommodation
# ---------------------------------------------------------------------------


async def test_accommodation_happy_path_interlaken(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(interlaken_page()))
    result = await find_accommodation_impl(
        client,
        FindAccommodationInput(
            near=INTERLAKEN,
            stars_min=4,
            garni=True,
            price_range="Mittel",
            amenities=["WiFi"],
            accessible=True,
        ),
    )

    body = _body(route)
    assert body["type"] == ["LodgingBusiness"]
    assert body["scoringReferencePoint"] == "7.8632,46.6863"
    assert body["starRatingValue"] == [4.0, 4.5, 5.0]
    assert body["starRatingGarni"] == [True]
    assert body["priceRange"] == [2]  # the facet value, not the display name
    assert body["amenityFeature"] == ["WiFi"]
    assert body["sourcePartner"] == ["pi", "okgo"]

    assert result.upstream_count == 3093
    du_nord = result.hits[0]
    assert du_nord.name == "Hotel Du Nord"
    assert du_nord.stars == 4.0 and du_nord.garni is True and du_nord.superior is False
    assert du_nord.distance_km is not None and du_nord.distance_km < 2
    assert "Ginto" in du_nord.accessibility_sources
    assert du_nord.attribution.provider == "HotellerieSuisse"
    assert du_nord.website == "http://www.hotel-dunord.ch"
    assert result.disclaimer and "HotellerieSuisse" in result.disclaimer


def test_accommodation_needs_near_or_locality() -> None:
    with pytest.raises(ValidationError):
        FindAccommodationInput(stars_min=3)


async def test_accommodation_filters_withheld_and_test_objects(api_mock, client) -> None:
    page = interlaken_page()
    page["values"] += [all_rights_reserved_event(), demo_event()]
    api_mock.post("/search").mock(return_value=json_response(page))
    result = await find_accommodation_impl(client, FindAccommodationInput(locality="Interlaken"))
    assert result.excluded_by_license == 1
    assert result.excluded_test_objects == 1
    assert result.returned == 5


async def test_accommodation_empty_result_carries_the_hint(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await find_accommodation_impl(
        client, FindAccommodationInput(locality="Grindelwlad", stars_min=5)
    )
    assert result.hint == ACCOMMODATION_EMPTY_HINT
    assert result.disclaimer is None


# ---------------------------------------------------------------------------
# Tool 4 — find_tours
# ---------------------------------------------------------------------------


def _tour(**extra: Any) -> dict[str, Any]:
    hit = {
        "identifier": "tou_ctd_planetenweg",
        "name": "Glarner Planetenweg",
        "type": "Tour",
        "additionalType": "ThemeTrail",
        "length": 8500,
        "elevation": {"ascent": 210, "descent": 190},
        "rating": {"difficulty": 1},
        "time": 150,
        "geo": {"latitude": 47.04, "longitude": 9.07},
        "dataGovernance": _governance("ctd", "contentdesk", "CC BY-SA"),
    }
    hit.update(extra)
    return hit


def _area_facet(values: list[dict[str, Any]]) -> dict[str, Any]:
    return {"count": 345, "values": [], "facets": {"containedInPlace/id": {"values": values}}}


async def test_tours_body_and_hit_fields(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 18, "values": [_tour()], "facets": {}})
    )
    result = await find_tours_impl(
        client,
        FindToursInput(
            kind="hiking",
            difficulty_max=2,
            length_km_max=10,
            ascent_m_max=300,
            season_month=9,
        ),
    )

    body = _body(route)
    assert body["type"] == ["Tour"]
    assert body["leafType"] == [
        "HikingTrail",
        "Route",
        "Way",
        "Tour",
        "Longdistance",
        "NatureTrail",
        "ThemeTrail",
    ]
    assert "categoryTree" not in body
    assert body["filters"] == [
        "length le 10000 and elevation/ascent le 300 and rating/difficulty le 2"
    ]
    assert body["season"] == ["sep"]

    hit = result.hits[0]
    assert hit.length_km == 8.5
    assert (hit.ascent_m, hit.descent_m, hit.difficulty, hit.duration_min) == (210, 190, 1, 150)
    assert hit.provider == "contentdesk"
    assert hit.attribution.license == "CC BY-SA"


@pytest.mark.parametrize(
    ("kind", "category"),
    [
        ("winter", "sui_root|sui_01|sui_0110"),
        ("cycling", "sui_root|sui_01|sui_0102"),
        ("mtb", "sui_root|sui_01|sui_0102|sui_010205"),
    ],
)
async def test_tours_category_kinds_send_the_full_path(api_mock, client, kind, category) -> None:
    """The short code (`sui_0110`) answers 0 without an error; only the full path filters."""
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [_tour()], "facets": {}})
    )
    await find_tours_impl(client, FindToursInput(kind=kind))
    body = _body(route)
    assert body["categoryTree"] == [category]
    assert "leafType" not in body


def test_no_tour_kind_names_a_type_the_index_does_not_have() -> None:
    """The first mapping sent three types with zero tours. These are the measured ones."""
    from discover_swiss_mcp.tools import TOUR_KINDS

    measured = {
        "ThemeTrail", "Route", "NatureTrail", "Tour", "CrossCountry", "TobogganRun",
        "ViaFerrata", "ShipTour", "SkiSlope", "HikingTrail", "TrainTour", "BikeTrail",
        "Way", "CarTour", "GlacierTour", "HighTour", "Longdistance", "SegwayTour",
    }  # fmt: skip
    for mapping in TOUR_KINDS.values():
        assert set(mapping.get("leafType", [])) <= measured
        assert all(path.startswith("sui_root|") for path in mapping.get("categoryTree", []))


async def test_tours_kind_all_sends_no_leaf_type(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [_tour()], "facets": {}})
    )
    await find_tours_impl(client, FindToursInput())
    body = _body(route)
    assert "leafType" not in body
    assert "categoryTree" not in body
    assert "filters" not in body


async def test_tours_region_resolves_to_an_area_filter(api_mock, client) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        if body.get("facets"):
            return json_response(
                _area_facet(
                    [
                        {"value": "osm_51701", "name": "Schweiz", "count": 351},
                        {"value": "ds_glarnerland", "name": "Glarnerland", "count": 345},
                    ]
                )
            )
        assert body["containedInPlace"] == ["ds_glarnerland"]
        return json_response({"count": 117, "values": [_tour()], "facets": {}})

    api_mock.post("/search").mock(side_effect=respond)
    result = await find_tours_impl(client, FindToursInput(region="Glarnerland"))

    assert result.area is not None
    assert result.area.identifier == "ds_glarnerland"
    assert result.area.ambiguous is False
    assert result.upstream_count == 117
    assert result.applied["containedInPlace"] == ["ds_glarnerland"]


async def test_tours_unresolved_region_does_not_search_everywhere(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response(
            _area_facet([{"value": "osm_51701", "name": "Schweiz", "count": 351}])
        )
    )
    result = await find_tours_impl(client, FindToursInput(region="Berner Oberland"))

    assert route.call_count == 1  # the area lookup, and no tour search after it
    assert result.hits == []
    assert result.area is not None and result.area.identifier is None
    assert result.hint and "No tour search was run" in result.hint


async def test_tours_radius_joins_the_odata_conditions(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [_tour()], "facets": {}})
    )
    near = GeoPoint(lat=46.9985, lon=9.0023)
    await find_tours_impl(client, FindToursInput(near=near, radius_km=15, difficulty_max=1))
    body = _body(route)
    assert body["filters"] == [
        "rating/difficulty le 1 and geo.distance(geo, geography'POINT(9.0023 46.9985)') le 15.0"
    ]
    assert body["scoringReferencePoint"] == "9.0023,46.9985"


async def test_tours_empty_result_carries_the_hint(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await find_tours_impl(client, FindToursInput(locality="Grindelwald"))
    assert result.hint == TOURS_EMPTY_HINT


async def test_tours_missing_measurements_stay_none(api_mock, client) -> None:
    """RailAway products carry no length or elevation — None, not zero."""
    railaway = _tour(length=None, elevation=None, rating=None, time=None)
    api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [railaway], "facets": {}})
    )
    result = await find_tours_impl(client, FindToursInput())
    hit = result.hits[0]
    assert (hit.length_km, hit.ascent_m, hit.difficulty, hit.duration_min) == (
        None,
        None,
        None,
        None,
    )
