"""Client behaviour against recorded shapes — offline, via respx.

Every assertion here mirrors something the live probe of 2026-09-17 measured.
Where the published documentation says otherwise, the probe is what is tested:
the paging token is a string called ``nextPageToken``, an unknown facet name is
dropped without an error, and a 403 carrying «quota» is a state rather than a
failure to retry.
"""

from __future__ import annotations

import asyncio
import time

import httpx
import pytest
from conftest import json_response, probe_fixture

from discover_swiss_mcp import client as client_module
from discover_swiss_mcp import net
from discover_swiss_mcp.client import (
    RETRY_DELAYS,
    SEARCH_SELECT_FIELDS,
    AuthorizationError,
    QuotaExhaustedError,
    SearchUnavailableError,
    UpstreamUnavailableError,
    distance_km,
    filter_by_distance,
)

# --------------------------------------------------------------------------
# Constants measured in the probe
# --------------------------------------------------------------------------


def test_search_select_is_the_verified_whitelist() -> None:
    """46 of the 48 IndexResponse fields; the other two answer 400."""
    assert len(SEARCH_SELECT_FIELDS) == 46
    assert len(set(SEARCH_SELECT_FIELDS)) == 46
    assert "containedInPlace" not in SEARCH_SELECT_FIELDS
    assert "context" not in SEARCH_SELECT_FIELDS


# --------------------------------------------------------------------------
# Search
# --------------------------------------------------------------------------


async def test_search_sends_project_as_an_array(api_mock, client) -> None:
    """Without `project` the endpoint answers 401 — so it is never the caller's."""
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 3, "values": [{"identifier": "a"}], "facets": {}})
    )
    result = await client.search({"searchText": "Landesmuseum", "resultsPerPage": 10})

    body = route.calls.last.request.read().decode()
    assert '"project":["dsod-content"]' in body.replace(" ", "")
    assert result.count == 3
    assert result.provenance == "live_api"


async def test_search_project_cannot_be_overridden_by_the_caller(api_mock, client) -> None:
    route = api_mock.post("/search").mock(return_value=json_response({"count": 0, "values": []}))
    await client.search({"project": ["demo-web"], "searchText": "x"})

    body = route.calls.last.request.read().decode().replace(" ", "")
    assert '"project":["dsod-content"]' in body
    assert "demo-web" not in body


async def test_search_second_identical_call_comes_from_the_cache(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [{"identifier": "a"}], "facets": {}})
    )
    first = await client.search({"searchText": "Rigi"})
    second = await client.search({"searchText": "Rigi"})

    assert route.call_count == 1
    assert first.provenance == "live_api"
    assert second.provenance == "cached"
    assert second.count == 1


async def test_missing_facets_are_reported_not_swallowed(api_mock, client) -> None:
    """An unknown facet name is dropped silently. The silence is the finding."""
    recorded = probe_fixture("probe_detail_out", "search_facets.json")
    api_mock.post("/search").mock(return_value=json_response(recorded))

    result = await client.search(
        {
            "resultsPerPage": 1,
            "facets": [
                {"name": "leafType", "count": 25},
                {"name": "containedInPlace", "count": 15},
                {"name": "sourcePartner", "count": 15},
                {"name": "ratingDifficulty", "count": 5},
                {"name": "season", "count": 12},
                {"name": "priceRange", "count": 5},
            ],
        }
    )

    # The two filterPropertyName spellings came back as nothing at all.
    assert result.missing_facets == ["containedInPlace", "ratingDifficulty"]
    assert "leafType" in result.facets
    assert result.count == 20817


async def test_facet_request_key_overrides_the_response_name(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {"tag1": {"values": []}}})
    )
    result = await client.search(
        {"facets": [{"key": "tag1", "name": "tag"}, {"key": "tag2", "name": "tag"}]}
    )
    assert result.missing_facets == ["tag2"]


# --------------------------------------------------------------------------
# Paging
# --------------------------------------------------------------------------


async def test_paging_follows_next_page_token_and_stops(api_mock, client) -> None:
    """`hasNextPage` is a bool, `nextPageToken` the string. Only the string pages."""
    pages = [
        json_response(
            {
                "hasNextPage": True,
                "nextPageToken": "TOKEN-1",
                "count": 3,
                "data": [{"identifier": "a"}],
            }
        ),
        json_response(
            {"hasNextPage": True, "nextPageToken": "TOKEN-2", "data": [{"identifier": "b"}]}
        ),
        json_response({"hasNextPage": False, "data": [{"identifier": "c"}]}),
    ]
    route = api_mock.get("/accommodations").mock(side_effect=pages)

    collected: list[dict] = []
    token: str | None = None
    while True:
        page = await client.list_endpoint(
            "accommodations", {"top": 1000, "continuationToken": token}
        )
        collected.extend(page.data)
        if not page.has_next_page or not page.next_token:
            break
        token = page.next_token

    assert [row["identifier"] for row in collected] == ["a", "b", "c"]
    assert route.call_count == 3
    assert "continuationToken=TOKEN-1" in str(route.calls[1].request.url)
    # `top=1000` does not mean 1000 rows — the token is what completes a set.
    assert "top=1000" in str(route.calls[0].request.url)


async def test_first_page_counts_and_later_pages_do_not(api_mock, client) -> None:
    route = api_mock.get("/webcams").mock(
        return_value=json_response({"hasNextPage": False, "count": 73, "data": []})
    )
    first = await client.list_endpoint("webcams")
    assert first.total == 73
    assert "includeCount=true" in str(route.calls[0].request.url)

    await client.list_endpoint("webcams", {"continuationToken": "TOKEN"})
    assert "includeCount=false" in str(route.calls[1].request.url)


async def test_list_endpoint_refuses_an_unknown_collection(client) -> None:
    with pytest.raises(client_module.UpstreamRejectedError):
        await client.list_endpoint("../admin")


async def test_list_endpoint_sends_project_top_and_select(api_mock, client) -> None:
    route = api_mock.get("/tours").mock(return_value=json_response({"data": []}))
    await client.list_endpoint("tours")
    url = str(route.calls.last.request.url)
    assert "project=dsod-content" in url
    assert "top=200" in url
    assert "select=" in url


def test_list_select_carries_the_measured_fields() -> None:
    """Fifteen fields, each one answered 200 live — none of them assumed.

    The last six were verified on 2026-09-23 against `/lodgingbusinesses`,
    `/civicStructures` and `/webcams`. A field added without that check can 400
    a whole page on one endpoint while working on another.
    """
    from discover_swiss_mcp.client import LIST_SELECT_FIELDS

    assert len(LIST_SELECT_FIELDS) == len(set(LIST_SELECT_FIELDS)) == 15
    for field in ("address", "url", "link", "image", "lastModified", "telephone"):
        assert field in LIST_SELECT_FIELDS
    # The fallback is useless without these two: a name and a coordinate is not
    # an answer to "where is it and how do I reach it".
    assert "address" in LIST_SELECT_FIELDS and "url" in LIST_SELECT_FIELDS


# --------------------------------------------------------------------------
# Detail
# --------------------------------------------------------------------------


async def test_get_vertex_returns_none_only_for_404(api_mock, client) -> None:
    api_mock.get("/vertices/does-not-exist").mock(return_value=httpx.Response(404))
    assert await client.get_vertex("does-not-exist") is None


async def test_get_vertex_passes_a_removed_object_through(api_mock, client) -> None:
    """«This existed and is gone» is an answer; `None` would hide it."""
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response({"identifier": "civ_px9-s28_bggg", "removed": True})
    )
    obj = await client.get_vertex("civ_px9-s28_bggg")
    assert obj is not None
    assert obj["removed"] is True


async def test_get_vertex_refuses_a_path_traversal_identifier(client) -> None:
    with pytest.raises(client_module.UpstreamRejectedError):
        await client.get_vertex("../../projects")


async def test_get_vertex_is_cached(api_mock, client) -> None:
    route = api_mock.get("/vertices/log_x8-tdgf_bcfch").mock(
        return_value=json_response({"identifier": "log_x8-tdgf_bcfch", "name": "Hotel Du Nord"})
    )
    await client.get_vertex("log_x8-tdgf_bcfch")
    await client.get_vertex("log_x8-tdgf_bcfch")
    assert route.call_count == 1


# --------------------------------------------------------------------------
# Retry policy
# --------------------------------------------------------------------------


async def test_5xx_climbs_the_ladder_then_fails(api_mock, client, sleeps) -> None:
    route = api_mock.get("/webcams").mock(return_value=httpx.Response(503))

    with pytest.raises(UpstreamUnavailableError):
        await client.list_endpoint("webcams")

    assert sleeps == list(RETRY_DELAYS) == [2.0, 4.0, 8.0]
    assert route.call_count == len(RETRY_DELAYS) + 1


async def test_5xx_then_success_stops_retrying(api_mock, client, sleeps) -> None:
    api_mock.get("/webcams").mock(
        side_effect=[httpx.Response(500), json_response({"data": [{"identifier": "a"}]})]
    )
    page = await client.list_endpoint("webcams")
    assert [row["identifier"] for row in page.data] == ["a"]
    assert sleeps == [2.0]


async def test_network_error_uses_the_same_ladder(api_mock, client, sleeps) -> None:
    api_mock.get("/webcams").mock(side_effect=httpx.ConnectError("no route"))
    with pytest.raises(UpstreamUnavailableError):
        await client.list_endpoint("webcams")
    assert sleeps == [2.0, 4.0, 8.0]


async def test_timeout_is_a_clean_error_not_a_traceback(api_mock, client, sleeps) -> None:
    api_mock.get("/webcams").mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(UpstreamUnavailableError) as excinfo:
        await client.list_endpoint("webcams")
    assert "discover.swiss" in str(excinfo.value)


async def test_429_waits_the_named_seconds_and_retries_once(api_mock, client, sleeps) -> None:
    api_mock.get("/webcams").mock(
        side_effect=[
            json_response(
                {"message": "Rate limit is exceeded. Try again in 5 seconds."}, status=429
            ),
            json_response({"data": [{"identifier": "a"}]}),
        ]
    )
    page = await client.list_endpoint("webcams")
    # Five named, one on top: arriving exactly on the boundary earns a second 429.
    assert sleeps == [6.0]
    assert len(page.data) == 1


async def test_429_reads_retry_after_from_the_header_when_the_body_names_none(
    api_mock, client, sleeps
) -> None:
    """The header is the fallback; a mutation that drops it falls to the 60 s default."""
    api_mock.get("/webcams").mock(
        side_effect=[
            httpx.Response(
                429, json={"message": "Too many requests."}, headers={"Retry-After": "7"}
            ),
            json_response({"data": [{"identifier": "a"}]}),
        ]
    )
    page = await client.list_endpoint("webcams")
    assert sleeps == [8.0]
    assert len(page.data) == 1


async def test_429_twice_gives_up_instead_of_looping(api_mock, client, sleeps) -> None:
    api_mock.get("/webcams").mock(
        return_value=json_response(
            {"message": "Rate limit is exceeded. Try again in 5 seconds."}, status=429
        )
    )
    with pytest.raises(client_module.RateLimitedError) as excinfo:
        await client.list_endpoint("webcams")
    assert sleeps == [6.0]
    assert excinfo.value.retry_after == 6.0
    assert excinfo.value.degraded == "rate_limited"


async def test_4xx_is_not_retried(api_mock, client, sleeps) -> None:
    route = api_mock.get("/webcams").mock(
        return_value=json_response({"message": "Supplied project doesn't exist"}, status=400)
    )
    with pytest.raises(client_module.UpstreamRejectedError):
        await client.list_endpoint("webcams")
    assert route.call_count == 1
    assert sleeps == []


# --------------------------------------------------------------------------
# Quota and search entitlement
# --------------------------------------------------------------------------


async def test_403_quota_is_a_state_not_a_retry(api_mock, client, sleeps) -> None:
    route = api_mock.get("/webcams").mock(
        return_value=json_response({"message": "Out of call volume quota."}, status=403)
    )
    with pytest.raises(QuotaExhaustedError) as excinfo:
        await client.list_endpoint("webcams")

    assert route.call_count == 1
    assert sleeps == []
    assert excinfo.value.degraded == "quota_exhausted"

    status = await client.status()
    assert status["quota_exhausted_since"] is not None
    assert status["reachable"] is False
    # And the state sticks: a second call does not spend another request.
    with pytest.raises(QuotaExhaustedError):
        await client.list_endpoint("webcams")
    assert route.call_count == 1


async def test_403_without_quota_outside_search_is_an_auth_error(api_mock, client) -> None:
    api_mock.get("/webcams").mock(
        return_value=json_response(
            {"message": "Access denied due to invalid subscription key."}, status=403
        )
    )
    with pytest.raises(AuthorizationError):
        await client.list_endpoint("webcams")


async def test_refused_search_turns_on_the_fallback_for_ten_minutes(api_mock, client) -> None:
    """The documented state, live since never — and the reason for the fallback."""
    search_route = api_mock.post("/search").mock(
        return_value=json_response(
            {"message": "You can't use the search functionality"}, status=403
        )
    )
    with pytest.raises(SearchUnavailableError) as excinfo:
        await client.search({"searchText": "Landesmuseum"})

    assert excinfo.value.degraded == "search_unavailable"
    assert client.search_available is False

    # No second request is spent on an endpoint known to refuse.
    with pytest.raises(SearchUnavailableError):
        await client.search({"searchText": "Grindelwald"})
    assert search_route.call_count == 1

    fallback = api_mock.get("/civicStructures").mock(
        return_value=json_response({"hasNextPage": False, "data": [{"identifier": "civ_1"}]})
    )
    page = await client.list_fallback("civicStructures", contained_in_place="ds_glarnerland")
    assert page.provenance == "list_fallback"
    assert "containedInPlace=ds_glarnerland" in str(fallback.calls.last.request.url)


async def test_search_becomes_available_again_after_the_window(
    api_mock, client, monkeypatch
) -> None:
    api_mock.post("/search").mock(
        side_effect=[
            json_response({"message": "no search for you"}, status=401),
            json_response({"count": 1, "values": [{"identifier": "a"}]}),
        ]
    )
    with pytest.raises(SearchUnavailableError):
        await client.search({"searchText": "x"})

    # Move past the ten-minute window without waiting for it. The expiry is read
    # once, up front: the `search_available` property clears the field as soon as
    # it has passed, so a lambda reading it lazily reads `None` on the next call.
    expiry = client._search_unavailable_until
    monkeypatch.setattr(client_module, "_monotonic", lambda: expiry + 1.0)
    result = await client.search({"searchText": "x"})
    assert result.count == 1
    assert client.search_available is True


# --------------------------------------------------------------------------
# Areas
# --------------------------------------------------------------------------


async def test_resolve_area_matches_the_name_exactly(api_mock, client) -> None:
    recorded = probe_fixture("probe_verify_out", "f5_facet.json")["response"]
    api_mock.post("/search").mock(return_value=json_response(recorded))

    lookup = await client.resolve_area("Glarnerland")
    assert lookup.identifier == "ds_glarnerland"
    assert lookup.name == "Glarnerland"
    assert lookup.hint is None


# The facet as `probes/probe_open.py` read it live on 2026-09-23: two areas
# carry the exact name «Zürich», and the larger is not the first in the list.
ZURICH_FACET = {
    "count": 1,
    "values": [{"identifier": "x"}],
    "facets": {
        "containedInPlace/id": {
            "values": [
                {"value": "osm_51701", "name": "Schweiz", "count": 1073},
                {"value": "kire_zurich", "name": "Zürich", "count": 785},
                {"value": "ds_kire", "name": "Kinderregion", "count": 878},
                {"value": "osm_1690227", "name": "Zürich", "count": 894},
            ]
        }
    },
}


async def test_two_areas_of_the_same_name_are_not_chosen_silently(api_mock, client) -> None:
    """«Zürich» is two areas. Picking one without saying so is the move to avoid."""
    api_mock.post("/search").mock(return_value=json_response(ZURICH_FACET))

    lookup = await client.resolve_area("Zürich")

    # The larger wins — a caller needs an id — but never quietly.
    assert lookup.identifier == "osm_1690227"
    assert lookup.ambiguous is True
    assert [s.identifier for s in lookup.suggestions] == ["kire_zurich"]
    assert "2 areas are named" in lookup.hint
    assert "kire_zurich" in lookup.hint


async def test_a_unique_name_is_not_flagged_ambiguous(api_mock, client) -> None:
    recorded = probe_fixture("probe_verify_out", "f5_facet.json")["response"]
    api_mock.post("/search").mock(return_value=json_response(recorded))

    lookup = await client.resolve_area("Glarnerland")
    assert lookup.ambiguous is False
    assert lookup.suggestions == []


async def test_resolve_area_suggests_instead_of_guessing(api_mock, client) -> None:
    """The largest facet value is «Schweiz». Returning it would answer another question."""
    recorded = probe_fixture("probe_verify_out", "f5_facet.json")["response"]
    api_mock.post("/search").mock(return_value=json_response(recorded))

    lookup = await client.resolve_area("Glarner Land")
    assert lookup.identifier is None
    assert [s.name for s in lookup.suggestions] == ["Schweiz", "Glarnerland", "Glarus"]
    assert "Glarner Land" in lookup.hint


# --------------------------------------------------------------------------
# Status and rate budget
# --------------------------------------------------------------------------


async def test_status_reports_reachability_and_counters(api_mock, client) -> None:
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    status = await client.status()
    assert status["reachable"] is True
    assert status["search_available"] is True
    assert status["calls_last_minute"] == 1
    assert status["quota_exhausted_since"] is None
    assert status["last_success"] is not None


class FakeClock:
    """A clock that moves only when told to — or when a wait is taken."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


async def test_the_bucket_brakes_before_the_gateway_does(
    api_mock, client, sleeps, monkeypatch
) -> None:
    clock = FakeClock()
    monkeypatch.setattr(client_module, "_monotonic", clock)
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    for _ in range(client_module.RATE_LIMIT_PER_MINUTE):
        await client.status()
    assert sleeps == []

    # 50 s later the oldest slot frees in about 10 s — inside the budget, so
    # the 56th call waits for the window instead of earning a 429.
    clock.now += 50.0
    state = await client.status()
    assert state["reachable"] is True
    assert len(sleeps) == 1
    assert 9 < sleeps[0] < 11


async def test_a_bucket_wait_beyond_the_budget_is_not_taken(
    api_mock, client, sleeps, monkeypatch
) -> None:
    """Waiting a full minute for a slot would outlive the MCP client (audit ARCH-014)."""
    clock = FakeClock()
    monkeypatch.setattr(client_module, "_monotonic", clock)
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    for _ in range(client_module.RATE_LIMIT_PER_MINUTE):
        await client.status()
    # Same instant: the next slot is a full minute away.
    state = await client.status()
    assert sleeps == []
    assert state["reachable"] is False
    assert state["rate_limited_for"] > client_module.TOTAL_BUDGET


async def test_the_request_gets_only_what_the_bucket_wait_left_of_the_budget(
    api_mock, client, monkeypatch
) -> None:
    """Re-verification of OPS-010: `remaining` was measured before the bucket wait.

    The bucket takes a wait of 24.99 s out of 25; the request that follows may
    use the 0.01 s left, not a fresh 25 s. The slow upstream (1 s, real time)
    must therefore be cut off at once.
    """
    clock = FakeClock()
    monkeypatch.setattr(client_module, "_monotonic", clock)
    waits: list[float] = []

    async def _advancing_sleep(seconds: float) -> None:
        waits.append(seconds)
        clock.now += seconds

    monkeypatch.setattr(client_module, "_sleep", _advancing_sleep)
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    for _ in range(client_module.RATE_LIMIT_PER_MINUTE):
        await client._call("GET", "/status")

    # The oldest slot frees 24.99 s from now: inside the 25 s budget, so taken.
    clock.now += client_module.RATE_LIMIT_WINDOW_SECONDS + 0.05 - 24.99

    async def _slow(_request):
        await asyncio.sleep(1.0)
        return httpx.Response(204)

    api_mock.get("/webcams").mock(side_effect=_slow)
    started = time.perf_counter()
    with pytest.raises(UpstreamUnavailableError):
        await client._call("GET", "/webcams")
    assert time.perf_counter() - started < 0.5
    assert waits and 24.9 < waits[0] < 25.0


async def test_a_429_wait_beyond_the_budget_ends_the_call_at_once(api_mock, client, sleeps) -> None:
    """The first version let a 429 extend the budget to about 55 s."""
    api_mock.get("/webcams").mock(
        return_value=json_response(
            {"message": "Rate limit is exceeded. Try again in 29 seconds."}, status=429
        )
    )
    with pytest.raises(client_module.RateLimitedError) as excinfo:
        await client.list_endpoint("webcams")
    assert sleeps == []
    assert excinfo.value.retry_after == 30.0


async def test_source_status_reports_a_rate_limit_as_such(api_mock, client, sleeps) -> None:
    """A pause the source asked for is not an outage."""
    from discover_swiss_mcp.tools import source_status_impl

    api_mock.get("/status").mock(
        return_value=json_response(
            {"message": "Rate limit is exceeded. Try again in 40 seconds."}, status=429
        )
    )
    status = await source_status_impl(client)
    assert status.degraded == "rate_limited"
    assert "41 seconds" in (status.hint or "")


async def test_a_dns_failure_is_retried_but_an_egress_block_is_not(
    api_mock, client, sleeps, monkeypatch
) -> None:
    """The retry pair of SEC-028: transient resolution vs. policy decision."""

    async def _no_dns(_host: str, _port: int) -> list[str]:
        raise net.ResolutionError("no answer")

    monkeypatch.setattr(net, "_resolve", _no_dns)
    with pytest.raises(UpstreamUnavailableError):
        await client._call("GET", "/status")
    assert sleeps == [2.0, 4.0, 8.0]

    sleeps.clear()

    async def _private(_host: str, _port: int) -> list[str]:
        return ["10.0.0.5"]

    monkeypatch.setattr(net, "_resolve", _private)
    with pytest.raises(net.EgressError):
        await client._call("GET", "/status")
    assert sleeps == []


# --------------------------------------------------------------------------
# Fallback geometry
# --------------------------------------------------------------------------


def test_distance_km_matches_a_known_pair() -> None:
    # Zurich HB to Interlaken, roughly 93 km as the crow flies.
    zurich = (47.378914, 8.540993)
    interlaken = (46.688237, 7.862343)
    assert 90 < distance_km(*zurich, *interlaken) < 96


def test_filter_by_distance_sorts_and_drops_the_coordinateless() -> None:
    rows = [
        {"identifier": "far", "geo": {"latitude": 47.0, "longitude": 9.5}},
        {"identifier": "near", "geo": {"latitude": 47.379, "longitude": 8.541}},
        {"identifier": "nogeo"},
        {"identifier": "mid", "geo": {"latitude": 47.4, "longitude": 8.6}},
    ]
    kept = filter_by_distance(rows, 47.378914, 8.540993, radius_km=25)
    assert [row["identifier"] for row in kept] == ["near", "mid"]


# --------------------------------------------------------------------------
# Time seams under real time (audit OPS-010)
# --------------------------------------------------------------------------


async def test_the_budget_holds_under_real_time(api_mock, client, monkeypatch) -> None:
    """A slow upstream ends the call at the budget — measured on the wall clock.

    Every other budget test runs on the `sleeps` fixture, where a wait costs
    nothing; there, TOTAL_BUDGET = 1e9 survived all 215 tests. This one uses
    real time and fails under that mutation.
    """
    monkeypatch.setattr(client_module, "TOTAL_BUDGET", 0.3)

    async def _slow(_request):
        await asyncio.sleep(2.0)
        return httpx.Response(204)

    api_mock.get("/status").mock(side_effect=_slow)
    started = time.perf_counter()
    with pytest.raises(UpstreamUnavailableError):
        await client._call("GET", "/status")
    elapsed = time.perf_counter() - started
    # Upper bound with room for a slow CI runner; the slow upstream takes 2 s.
    assert 0.25 < elapsed < 1.5


async def test_the_sleep_fixture_does_not_silence_real_sleep(sleeps) -> None:
    """The fixture replaces the client's seam, not asyncio.sleep for everyone."""
    started = time.perf_counter()
    await asyncio.sleep(0.05)
    assert time.perf_counter() - started >= 0.04
    await client_module._sleep(7.0)
    assert sleeps == [7.0]


def test_the_time_seams_default_to_the_real_clock() -> None:
    assert client_module._monotonic is time.monotonic
    assert client_module._sleep is asyncio.sleep
