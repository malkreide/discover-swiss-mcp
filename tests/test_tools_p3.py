"""The four P3 tools and the list fallback, driven through their ``*_impl`` functions.

Offline, via respx, against recorded shapes where the probe recorded them:

* events: `probe_verify_out/f4_odata.json` (18 events, «Schweizer Genusswoche»
  with the 2099 sentinel, «Demo Event» live in the index),
* webcams: `probe_verify_out/f3_webcam_sg.json` (17 within 25 km of St. Gallen)
  plus `probe_open_out/select_row_webcams.json` for governance, link and image,
* facets: `probe_verify_out/f1_odata.json` (all eight OData names answered)
  and `probe_verify_out/f5_facet.json` for the «Glarnerland» area lookup,
* list rows: `probe_open_out/select_row_civicStructures.json`.

The recorded search answers were taken with a narrow ``select``; where a hit
needs fields the recording lacks (schedule, organiser, governance), they are
added in the recorded shape and the identifiers and names stay the recorded
ones.
"""

from __future__ import annotations

import copy
import json
from datetime import date
from typing import Any

import httpx
import pytest
from conftest import json_response, probe_fixture
from pydantic import ValidationError

from discover_swiss_mcp.client import VERIFIED_FACETS, DiscoverSwissClient, odata_facet_names
from discover_swiss_mcp.config import ConfigError, load_settings
from discover_swiss_mcp.tools import (
    EVENTS_EMPTY_HINT,
    FALLBACK_HINT,
    FALLBACK_MAX_CALLS,
    MISSING_FACETS_HINT,
    SNAPSHOT_NOTE,
    UNKNOWN_FACETS_HINT,
    ExploreAreaInput,
    FindAccommodationInput,
    FindEventsInput,
    GeoPoint,
    SearchInput,
    WebcamsNearInput,
    explore_area_impl,
    fallback_endpoints,
    find_accommodation_impl,
    find_events_impl,
    search_impl,
    source_status_impl,
    webcams_near_impl,
)

ST_GALLEN = GeoPoint(lat=47.4245, lon=9.3767)
ZURICH_HB = GeoPoint(lat=47.3779, lon=8.5403)
RANGE = {"from_date": date(2026, 9, 17), "to_date": date(2026, 12, 16)}


def _body(route) -> dict[str, Any]:
    return json.loads(route.calls.last.request.read())


def _governance(acronym: str, name: str, licence: str) -> dict[str, Any]:
    partner = {
        "acronym": acronym,
        "identifier": acronym,
        "type": "schema.org/Partner",
        "name": name,
    }
    return {"origin": [{"datasource": acronym, "license": licence, "provider": partner}]}


CTD = _governance("tso-ctd", "contentdesk.io by TSO AG", "CC BY-SA")


# ---------------------------------------------------------------------------
# Tool 5 — find_events
# ---------------------------------------------------------------------------


def events_page() -> dict[str, Any]:
    """`f4_odata.json` (count 18) with schedule, organiser and governance per hit."""
    recorded = probe_fixture("probe_verify_out", "f4_odata.json")["response"]
    extra: dict[str, dict[str, Any]] = {
        "Schweizer Genusswoche": {
            "schedule": [{"startDate": "2026-09-17", "endDate": "2026-09-27"}],
            "organizer": {"name": "Schweizer Genusswoche"},
        },
        "Universität St.Gallen Promotionsfeier": {
            "schedule": [{"startDate": "2027-02-26", "startTime": "14:00:00"}],
            "address": {"addressLocality": "St.Gallen"},
            "organizer": {"name": "Universität St.Gallen"},
            "link": [{"type": "WebHomepage", "url": "https://www.unisg.ch"}],
        },
        "Demo Event": {
            "address": {"streetAddress": "Strasse 1", "postalCode": "PLZ", "addressLocality": "Ort"}
        },
    }
    values = []
    for hit in recorded["values"]:
        hit = {**hit, "type": "Event", "dataGovernance": CTD, **extra.get(hit["name"], {})}
        values.append(hit)
    # A Guidle event as the probe found them: all rights reserved.
    values.append(
        {
            "identifier": "eve_gdl_arr",
            "name": "Konzert im Park",
            "type": "Event",
            "nextOccurrence": "2026-10-03T19:30:00+00:00",
            "dataGovernance": _governance("gdl", "Guidle", "C-All-Rights-Reserved"),
        }
    )
    return {"count": recorded["count"], "values": values, "facets": {}}


async def test_events_body_uses_the_odata_schedule_filter(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(events_page()))
    await find_events_impl(client, FindEventsInput(**RANGE))

    body = _body(route)
    assert body["type"] == ["Event"]
    assert body["filters"] == [
        "schedule/any(item: item/endDate ge 2026-09-17T00:00:00Z "
        "and item/startDate le 2026-12-16T23:59:59Z)"
    ]
    # The convenient filter miscounts (PROBE_VERIFY 4); it must never be sent.
    assert "scheduleStart" not in body
    assert "scheduleEnd" not in body
    assert body["project"] == ["dsod-content"]
    assert "schedule" in body["select"].split(",")


def test_events_default_range_is_thirty_days() -> None:
    params = FindEventsInput(from_date=date(2026, 9, 25))
    assert params.effective_to_date == date(2026, 10, 25)


def test_events_default_from_date_is_today_and_not_in_the_schema() -> None:
    """A literal default would be the build day and change the tool hash at midnight."""
    assert FindEventsInput().from_date is not None
    schema = FindEventsInput.model_json_schema()
    assert "default" not in schema["properties"]["from_date"]


def test_events_reversed_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FindEventsInput(from_date=date(2026, 10, 1), to_date=date(2026, 9, 1))


async def test_events_sentinel_is_date_open_never_2099(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=json_response(events_page()))
    result = await find_events_impl(client, FindEventsInput(**RANGE))

    week = next(h for h in result.hits if h.name == "Schweizer Genusswoche")
    assert week.next_occurrence is None
    assert week.date_open is True
    assert week.date_note == "Termin offen"
    assert "2099" not in result.model_dump_json()


async def test_events_date_note_follows_lang(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=json_response(events_page()))
    result = await find_events_impl(client, FindEventsInput(lang="en", **RANGE))
    week = next(h for h in result.hits if h.name == "Schweizer Genusswoche")
    assert week.date_note == "Date to be announced"


async def test_events_hit_fields(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=json_response(events_page()))
    result = await find_events_impl(client, FindEventsInput(**RANGE))

    uni = next(h for h in result.hits if h.name == "Universität St.Gallen Promotionsfeier")
    assert uni.next_occurrence == "2027-02-26T14:00:00+00:00"
    assert uni.start == "2027-02-26T14:00:00"
    assert uni.locality == "St.Gallen"
    assert uni.organizer_name == "Universität St.Gallen"
    assert uni.website == "https://www.unisg.ch"
    assert uni.attribution.license == "CC BY-SA"
    assert result.disclaimer and "discover.swiss" in result.disclaimer


async def test_events_missing_next_occurrence_falls_back_to_the_schedule(api_mock, client) -> None:
    hit = {
        "identifier": "eve_wt1_bbgefdccag",
        "name": "Öffentliche Genuss-Degustation im Breitenmoser Gustarium",
        "type": "Event",
        "schedule": [
            {"startDate": "2026-06-01", "endDate": "2026-06-01"},
            {"startDate": "2026-10-02", "startTime": "18:00", "endDate": "2026-10-02"},
        ],
        "dataGovernance": CTD,
    }
    api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [hit], "facets": {}})
    )
    result = await find_events_impl(client, FindEventsInput(**RANGE))

    event = result.hits[0]
    # The first entry still running on from_date, not the first entry overall.
    assert event.next_occurrence == "2026-10-02T18:00"
    assert event.date_open is False
    assert event.date_note is None


async def test_events_demo_and_guidle_are_withheld_and_counted(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=json_response(events_page()))
    result = await find_events_impl(client, FindEventsInput(**RANGE))

    names = {h.name for h in result.hits}
    assert "Demo Event" not in names
    assert "Konzert im Park" not in names
    assert result.excluded_test_objects == 1
    assert result.excluded_by_license == 1
    assert result.upstream_count == 18
    assert result.fetched == result.returned + 2


async def test_events_empty_result_carries_the_hint(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await find_events_impl(client, FindEventsInput(locality="Zürich", **RANGE))
    assert result.hint == EVENTS_EMPTY_HINT
    assert result.disclaimer is None


async def test_events_radius_joins_the_date_filter(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    await find_events_impl(client, FindEventsInput(near=ST_GALLEN, radius_km=10, **RANGE))
    (condition,) = _body(route)["filters"]
    assert condition.endswith(" and geo.distance(geo, geography'POINT(9.3767 47.4245)') le 10.0")
    assert _body(route)["scoringReferencePoint"] == "9.3767,47.4245"


async def test_events_region_resolves_to_an_area_filter(api_mock, client) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        if body.get("facets"):
            return json_response(
                {
                    "count": 5,
                    "values": [],
                    "facets": {
                        "containedInPlace/id": {
                            "values": [
                                {
                                    "value": "ds_appenzellerland",
                                    "name": "Appenzellerland",
                                    "count": 4,
                                }
                            ]
                        }
                    },
                }
            )
        assert body["containedInPlace"] == ["ds_appenzellerland"]
        return json_response({"count": 0, "values": [], "facets": {}})

    api_mock.post("/search").mock(side_effect=respond)
    result = await find_events_impl(client, FindEventsInput(region="Appenzellerland", **RANGE))
    assert result.area is not None and result.area.identifier == "ds_appenzellerland"


# ---------------------------------------------------------------------------
# Tool 6 — webcams_near
# ---------------------------------------------------------------------------


def webcams_page() -> dict[str, Any]:
    """`f3_webcam_sg.json` (count 17) with the recorded webcam's governance, link, image."""
    recorded = probe_fixture("probe_verify_out", "f3_webcam_sg.json")["response"]
    row = probe_fixture("probe_open_out", "select_row_webcams.json")
    values = [
        {
            **hit,
            "type": "Webcam",
            "dataGovernance": row["dataGovernance"],
            "link": row["link"],
            "image": row["image"],
        }
        for hit in recorded["values"]
    ]
    return {"count": recorded["count"], "values": values, "facets": {}}


async def test_webcams_body_is_a_real_radius(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response(webcams_page()))
    result = await webcams_near_impl(client, WebcamsNearInput(near=ST_GALLEN))

    body = _body(route)
    assert body["type"] == ["Webcam"]
    assert body["filters"] == ["geo.distance(geo, geography'POINT(9.3767 47.4245)') le 25.0"]
    assert body["scoringReferencePoint"] == "9.3767,47.4245"
    assert body["resultsPerPage"] == 20
    assert result.upstream_count == 17
    assert result.has_more is False


async def test_webcams_hit_separates_live_image_and_snapshot(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=json_response(webcams_page()))
    result = await webcams_near_impl(client, WebcamsNearInput(near=ST_GALLEN))

    first = result.hits[0]
    assert first.name == "Webcam St.Gallen, Kapfwaldweg"
    assert first.live_url == "https://www.sky-cam.ch/atzmaennig/seilpark/livebild.php"
    assert first.snapshot_url and first.snapshot_url.startswith("https://media-v2.discover.swiss/")
    assert first.snapshot_note == SNAPSHOT_NOTE
    assert first.distance_km is not None and first.distance_km < 5
    assert first.attribution.license == "CC BY-SA"


def test_webcams_need_near_or_region() -> None:
    with pytest.raises(ValidationError):
        WebcamsNearInput()


async def test_webcams_region_sends_no_radius(api_mock, client) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        if body.get("facets"):
            return json_response(
                {
                    "count": 1,
                    "values": [],
                    "facets": {
                        "containedInPlace/id": {
                            "values": [{"value": "ds_toggenburg", "name": "Toggenburg", "count": 9}]
                        }
                    },
                }
            )
        assert "filters" not in body
        assert body["containedInPlace"] == ["ds_toggenburg"]
        return json_response(webcams_page())

    api_mock.post("/search").mock(side_effect=respond)
    result = await webcams_near_impl(client, WebcamsNearInput(region="Toggenburg"))
    assert result.returned == 3
    assert result.hits[0].distance_km is None


async def test_webcams_empty_result_does_not_invite_an_invented_webcam(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await webcams_near_impl(
        client, WebcamsNearInput(near=GeoPoint(lat=46.0207, lon=7.7491))
    )
    assert result.hint is not None
    assert "Eastern Switzerland" in result.hint
    assert "do not invent" in result.hint


# ---------------------------------------------------------------------------
# Tool 7 — explore_area
# ---------------------------------------------------------------------------


def test_facet_aliases_map_to_odata_names() -> None:
    assert odata_facet_names(["containedInPlace", "ratingDifficulty", "addressLocality"]) == [
        "containedInPlace/id",
        "rating/difficulty",
        "address/addressLocality",
    ]
    # Duplicates after mapping collapse; unknown names pass through to be checked.
    assert odata_facet_names(["containedInPlace", "containedInPlace/id", "tag"]) == [
        "containedInPlace/id",
        "tag",
    ]


async def test_explore_default_facets_body(api_mock, client) -> None:
    recorded = probe_fixture("probe_verify_out", "f1_odata.json")["response"]
    route = api_mock.post("/search").mock(return_value=json_response(recorded))
    result = await explore_area_impl(client, ExploreAreaInput())

    body = _body(route)
    assert body["resultsPerPage"] == 1
    assert body["select"] == "identifier"
    assert [f["name"] for f in body["facets"]] == [
        "leafType",
        "sourcePartner",
        "season",
        "priceRange",
    ]
    assert result.total == 20773
    assert set(result.facets) == {"leafType", "sourcePartner", "season", "priceRange"}
    room = result.facets["leafType"][0]
    assert (room.value, room.label, room.count) == ("HotelRoom", "Hotelzimmer", 5314)
    assert result.missing_facets == []
    assert result.hint is None


async def test_explore_all_eight_verified_facets_come_back(api_mock, client) -> None:
    recorded = probe_fixture("probe_verify_out", "f1_odata.json")["response"]
    api_mock.post("/search").mock(return_value=json_response(recorded))
    result = await explore_area_impl(client, ExploreAreaInput(facets=list(VERIFIED_FACETS)))
    assert set(result.facets) == set(VERIFIED_FACETS)
    assert result.missing_facets == []


async def test_explore_short_names_are_mapped_before_sending(api_mock, client) -> None:
    recorded = probe_fixture("probe_verify_out", "f1_odata.json")["response"]
    route = api_mock.post("/search").mock(return_value=json_response(recorded))
    result = await explore_area_impl(
        client, ExploreAreaInput(facets=["containedInPlace", "ratingDifficulty"])
    )
    assert [f["name"] for f in _body(route)["facets"]] == [
        "containedInPlace/id",
        "rating/difficulty",
    ]
    assert result.missing_facets == []
    assert result.facets["containedInPlace/id"][0].value == "osm_51701"


async def test_explore_does_not_send_an_unknown_facet(api_mock, client) -> None:
    """Live 2026-09-26: an unknown facet name answers 400 for the whole request."""
    recorded = probe_fixture("probe_verify_out", "f1_odata.json")["response"]
    route = api_mock.post("/search").mock(return_value=json_response(recorded))
    result = await explore_area_impl(client, ExploreAreaInput(facets=["leafType", "difficultyX"]))

    assert [f["name"] for f in _body(route)["facets"]] == ["leafType"]
    assert result.missing_facets == ["difficultyX"]
    assert set(result.facets) == {"leafType"}
    assert result.hint == UNKNOWN_FACETS_HINT.format(names="difficultyX")


async def test_explore_only_unknown_facets_still_counts(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1661, "values": [], "facets": {}})
    )
    result = await explore_area_impl(client, ExploreAreaInput(facets=["difficultyX"]))
    assert "facets" not in _body(route)
    assert result.total == 1661
    assert result.missing_facets == ["difficultyX"]


async def test_explore_reports_a_sent_facet_that_did_not_come_back(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 5, "values": [], "facets": {"leafType": {}}})
    )
    result = await explore_area_impl(client, ExploreAreaInput(facets=["leafType", "season"]))
    assert result.missing_facets == ["season"]
    assert result.hint == MISSING_FACETS_HINT.format(names="season")
    assert "silently dropped by the upstream API" in result.hint


async def test_explore_region_glarnerland(api_mock, client) -> None:
    lookup = probe_fixture("probe_verify_out", "f5_facet.json")["response"]
    counted = copy.deepcopy(probe_fixture("probe_verify_out", "f1_odata.json")["response"])
    counted["count"] = 345

    def respond(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.read())
        if body.get("searchText") == "Glarnerland":
            return json_response(lookup)
        assert body["containedInPlace"] == ["ds_glarnerland"]
        return json_response(counted)

    api_mock.post("/search").mock(side_effect=respond)
    result = await explore_area_impl(client, ExploreAreaInput(region="Glarnerland"))

    assert result.area is not None and result.area.identifier == "ds_glarnerland"
    assert result.total == 345
    assert result.applied["containedInPlace"] == ["ds_glarnerland"]


async def test_explore_near_uses_the_default_radius(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    result = await explore_area_impl(client, ExploreAreaInput(near=ZURICH_HB))
    assert _body(route)["filters"] == [
        "geo.distance(geo, geography'POINT(8.5403 47.3779)') le 10.0"
    ]
    # Nothing came back at all: every requested facet is missing, and the empty
    # scope is named too.
    assert result.total == 0
    assert result.hint and "Nothing in this scope" in result.hint


# ---------------------------------------------------------------------------
# Tool 8 — source_status
# ---------------------------------------------------------------------------


async def test_status_reports_counters_and_index_total(api_mock, client) -> None:
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    route = api_mock.post("/search").mock(
        return_value=json_response(probe_fixture("probe_verify_out", "f1_odata.json")["response"])
    )

    status = await source_status_impl(client)

    assert status.api_key_configured is True
    assert status.reachable is True
    assert status.search_available is True
    assert status.index_total == 20773
    assert status.degraded is None
    assert status.project == "dsod-content"
    assert status.base_url == "https://api.discover.swiss/info/v2"
    assert status.calls_last_minute == 2
    assert status.last_success is not None
    assert status.cache_entries >= 1
    assert "hotels" in status.coverage.lower() or "Hotels" in status.coverage
    assert status.entitlement_note.endswith("written confirmation from discover.swiss: pending")

    # index_total is cached for an hour: a second status call does not search again.
    await source_status_impl(client)
    assert route.call_count == 1


async def test_status_entitlement_confirmed_from_the_environment(monkeypatch, api_mock) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_ENTITLEMENT_CONFIRMED", "2026-10-01")
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    api_mock.post("/search").mock(
        return_value=json_response({"count": 20817, "values": [], "facets": {"leafType": {}}})
    )
    instance = DiscoverSwissClient(load_settings())
    try:
        status = await source_status_impl(instance)
    finally:
        await instance.aclose()
    assert status.entitlement_note.endswith("confirmed 2026-10-01")


def test_status_entitlement_typo_is_a_config_error(monkeypatch) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_ENTITLEMENT_CONFIRMED", "yes")
    with pytest.raises(ConfigError):
        load_settings()


async def test_status_without_key_makes_no_call(monkeypatch, api_mock) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_KEY", "")
    status_route = api_mock.get("/status").mock(return_value=httpx.Response(204))
    instance = DiscoverSwissClient(load_settings(require_key=False))
    try:
        status = await source_status_impl(instance)
    finally:
        await instance.aclose()
    assert status.api_key_configured is False
    assert status_route.call_count == 0
    assert status.hint and "DISCOVER_SWISS_KEY" in status.hint


async def test_status_search_refused_is_degraded(api_mock, client) -> None:
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    status = await source_status_impl(client)
    assert status.reachable is True
    assert status.search_available is False
    assert status.index_total is None
    assert status.degraded == "search_unavailable"
    assert status.hint and "list_fallback" in status.hint


async def test_status_quota_exhausted(api_mock, client) -> None:
    api_mock.get("/status").mock(
        return_value=json_response({"message": "Out of call volume quota."}, status=403)
    )
    status = await source_status_impl(client)
    assert status.degraded == "quota_exhausted"
    assert status.monthly_quota_exhausted_since is not None


# ---------------------------------------------------------------------------
# List fallback in search and find_accommodation
# ---------------------------------------------------------------------------


def _list_row(identifier: str, name: str, lat: float, lon: float, **extra: Any) -> dict[str, Any]:
    """A list row in the recorded shape: root licence, copyright notice, provider."""
    row = copy.deepcopy(probe_fixture("probe_open_out", "select_row_civicStructures.json"))
    row.update(
        identifier=identifier,
        name=name,
        geo={"latitude": lat, "longitude": lon},
        additionalType="Museum",
    )
    row.update(extra)
    return row


def _list_page(rows: list[dict[str, Any]], total: int | None = None) -> dict[str, Any]:
    return {"count": len(rows) if total is None else total, "data": rows, "hasNextPage": False}


def _mock_lists(api_mock, pages: dict[str, dict[str, Any]]) -> dict[str, Any]:
    routes = {}
    for endpoint in (
        "places",
        "civicStructures",
        "foodEstablishments",
        "localbusinesses",
        "lodgingbusinesses",
    ):
        routes[endpoint] = api_mock.get(f"/{endpoint}").mock(
            return_value=json_response(pages.get(endpoint, _list_page([])))
        )
    return routes


async def test_search_refused_answers_from_the_lists(api_mock, client) -> None:
    search_route = api_mock.post("/search").mock(return_value=httpx.Response(401))
    wow = _list_row("civ_wow", "WOW Museum", 47.375022, 8.54033)
    far = _list_row("civ_far", "Museum in Winterthur", 47.4988, 8.7241)
    arr = _list_row("civ_arr", "Privatsammlung", 47.3769, 8.5417, license="C-All-Rights-Reserved")
    routes = _mock_lists(api_mock, {"civicStructures": _list_page([far, wow, arr])})

    result = await search_impl(client, SearchInput(query="Museum", near=ZURICH_HB, radius_km=2))

    assert search_route.call_count == 1
    assert all(route.call_count == 1 for route in routes.values())
    assert result.provenance == "list_fallback"
    assert result.degraded == "search_unavailable"
    assert result.hint is not None
    assert result.hint.startswith(FALLBACK_HINT)
    assert "Ignored in this mode: query" in result.hint
    assert result.ignored_parameters == ["query"]
    assert [h.identifier for h in result.hits] == ["civ_wow"]
    assert result.hits[0].distance_km is not None and result.hits[0].distance_km < 2
    assert result.hits[0].attribution.copyright_notice == "Zürich Tourismus www.zuerich.com"
    assert result.excluded_by_license == 1
    assert result.upstream_count == 2  # both rows within 2 km, before the licence gate
    assert result.applied["mode"] == "list_fallback"
    assert result.applied["scan_complete"] is True
    params = routes["civicStructures"].calls.last.request.url.params
    assert params["project"] == "dsod-content"
    assert params["top"] == "1000"


async def test_search_fallback_stays_on_the_lists_while_search_is_refused(api_mock, client) -> None:
    search_route = api_mock.post("/search").mock(return_value=httpx.Response(401))
    _mock_lists(api_mock, {})
    await search_impl(client, SearchInput(near=ZURICH_HB))
    await search_impl(client, SearchInput(near=ZURICH_HB, types=["Museum"]))
    # The refusal is remembered: the second call goes straight to the lists.
    assert search_route.call_count == 1


async def test_search_fallback_with_types_reads_only_their_collection(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    routes = _mock_lists(api_mock, {})
    result = await search_impl(client, SearchInput(types=["Museum"], near=ZURICH_HB))
    assert routes["civicStructures"].call_count == 1
    assert routes["lodgingbusinesses"].call_count == 0
    assert result.applied["endpoints"] == ["civicStructures"]
    assert result.applied["radius_km"] == 10.0


def test_unmapped_type_scans_every_collection() -> None:
    assert fallback_endpoints(["Museum", "Restaurant"]) == ("civicStructures", "foodEstablishments")
    assert len(fallback_endpoints(["Fireplace"])) == 5
    assert len(fallback_endpoints(None)) == 5


async def test_search_fallback_without_a_place_fetches_nothing(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    routes = _mock_lists(api_mock, {})
    result = await search_impl(client, SearchInput(query="Rigi"))
    assert all(route.call_count == 0 for route in routes.values())
    assert result.degraded == "search_unavailable"
    assert result.provenance == "list_fallback"
    assert result.hint and result.hint.startswith(FALLBACK_HINT)
    assert "nothing was fetched" in result.hint


async def test_search_fallback_matches_locality_exactly(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    wow = _list_row("civ_wow", "WOW Museum", 47.375022, 8.54033)
    baar = _list_row("civ_baar", "Museum Baar", 47.19, 8.52, address={"addressLocality": "Baar"})
    _mock_lists(api_mock, {"civicStructures": _list_page([wow, baar])})
    result = await search_impl(client, SearchInput(locality="zürich"))
    assert [h.identifier for h in result.hits] == ["civ_wow"]


async def test_search_fallback_reports_an_incomplete_scan(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    endless = {
        "count": 99999,
        "data": [_list_row("civ_wow", "WOW Museum", 47.375022, 8.54033)],
        "hasNextPage": True,
        "nextPageToken": "next",
    }
    routes = _mock_lists(api_mock, {"places": endless})
    result = await search_impl(client, SearchInput(near=ZURICH_HB))

    assert routes["places"].call_count == FALLBACK_MAX_CALLS
    assert routes["lodgingbusinesses"].call_count == 0
    assert result.applied["scan_complete"] is False
    assert result.hint and "Results may be incomplete" in result.hint
    assert "lodgingbusinesses" in result.hint


async def test_accommodation_refused_answers_from_lodging_list(api_mock, client) -> None:
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    hotel = _list_row(
        "log_du_nord",
        "Hotel Du Nord",
        46.6877,
        7.8633,
        type="LodgingBusiness",
        additionalType="Hotel",
        license="CC BY",
        copyrightNotice="HotellerieSuisse",
    )
    routes = _mock_lists(api_mock, {"lodgingbusinesses": _list_page([hotel])})

    result = await find_accommodation_impl(
        client,
        FindAccommodationInput(
            near=GeoPoint(lat=46.6863, lon=7.8632), radius_km=5, stars_min=3, accessible=True
        ),
    )

    assert routes["lodgingbusinesses"].call_count == 1
    assert sum(r.call_count for r in routes.values()) == 1
    assert result.provenance == "list_fallback"
    assert result.degraded == "search_unavailable"
    assert result.hint and result.hint.startswith(FALLBACK_HINT)
    assert "stars_min" in result.hint and "accessible" in result.hint
    assert [h.name for h in result.hits] == ["Hotel Du Nord"]
    assert result.hits[0].stars is None  # the list does not carry it; never guessed
    assert result.disclaimer


async def test_accommodation_fallback_names_the_filters_it_could_not_apply(
    api_mock, client
) -> None:
    """The hits are wider than asked for; a field says so, not only a sentence (DRIFT-002)."""
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    hotel = _list_row("lod_nord", "Hotel Du Nord", 46.6866, 7.8621)
    routes = _mock_lists(api_mock, {"lodgingbusinesses": _list_page([hotel])})
    result = await find_accommodation_impl(
        client,
        FindAccommodationInput(
            near=GeoPoint(lat=46.6863, lon=7.8632), stars_min=3, accessible=True, amenities=["WiFi"]
        ),
    )
    assert result.provenance == "list_fallback"
    assert result.degraded == "search_unavailable"
    assert result.ignored_parameters == ["stars_min", "amenities", "accessible"]
    assert result.hint and "NOT filtered" in result.hint
    assert [h.identifier for h in result.hits] == ["lod_nord"]
    assert routes["lodgingbusinesses"].call_count == 1
    assert routes["civicStructures"].call_count == 0


async def test_a_fallback_without_ignored_filters_says_nothing_is_ignored(api_mock, client) -> None:
    """The counter-check: an empty list when every parameter was applied."""
    api_mock.post("/search").mock(return_value=httpx.Response(401))
    _mock_lists(api_mock, {})
    result = await find_accommodation_impl(
        client, FindAccommodationInput(near=GeoPoint(lat=46.6863, lon=7.8632))
    )
    assert result.ignored_parameters == []
