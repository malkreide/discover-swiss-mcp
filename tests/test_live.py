"""Live canaries against the real discover.swiss API (P4).

Every test here is marked ``live``. CI runs ``pytest -m "not live"`` and never
sees them; locally they run with a key from the environment and nowhere else::

    export DISCOVER_SWISS_KEY=...          # never in a committed file
    pytest -m live -rA                     # -rA prints every measured value

Without a key the whole module skips — a skip, not a pass, and the summary
line says so.

**What the floors are.** Each lower bound is roughly half of what the live
index held on 2026-09-17 (``probes/PROBE_REPORT_discover-swiss-mcp.md``,
sections 2, 4, 5 and 8; ``probes/PROBE_VERIFY_discover-swiss.md``). Half,
because the point is not to pin the index but to notice the day a tool
silently stops finding what is there: a renamed field, a scope parameter the
API starts defaulting differently, a filter that begins to match nothing. That
day the count does not drift by ten percent — it collapses.

**What these tests do not do.** They do not pin the index from above, and they
do not assert on ranking beyond the one distance canary the probe verified.

Budget: about twenty calls against the monthly 50'000.

The three autouse fixtures of ``conftest.py`` are overridden below, by name.
Left in place, they would put ``test-key`` into the environment and resolve
every host to a documentation address — a live test that can never reach the
API, and would fail in a way that looks like an outage.
"""

from __future__ import annotations

import os
import re
from datetime import timedelta

import pytest

from discover_swiss_mcp.client import DiscoverSwissClient
from discover_swiss_mcp.config import load_settings
from discover_swiss_mcp.tools import (
    ExploreAreaInput,
    FindAccommodationInput,
    FindEventsInput,
    FindToursInput,
    GeoPoint,
    GetDetailsInput,
    SearchInput,
    WebcamsNearInput,
    _today,
    explore_area_impl,
    find_accommodation_impl,
    find_events_impl,
    find_tours_impl,
    get_details_impl,
    search_impl,
    webcams_near_impl,
)

pytestmark = pytest.mark.live

# Reference points, WGS84. Interlaken as in the probe (Höheweg); St. Gallen at
# the main station.
INTERLAKEN = GeoPoint(lat=46.6863, lon=7.8632)
ST_GALLEN = GeoPoint(lat=47.4232, lon=9.3695)

# Landesmuseum Zürich — the detail fixture of the probe (PROBE_REPORT 5.1).
LANDESMUSEUM_ID = "civ_px9-s28_bggg"

# Partner acronym of Zürich Tourismus in the `sourcePartner` facet
# (search_facets.json: value «zht», name «Zürich Tourismus», 1'311). The
# acronym is what the filter takes, not the display name.
ZURICH_TOURISMUS = "zht"

# An HTML entity, named or numeric. After `html_to_text` there must be none.
ENTITY = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);")


# ---------------------------------------------------------------------------
# Fixtures: real key, real DNS
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def api_key() -> str:
    """The real key from the environment — or the module skips."""
    key = os.environ.get("DISCOVER_SWISS_KEY", "").strip()
    if not key:
        pytest.skip("DISCOVER_SWISS_KEY is not set; live canaries need a real key.")
    return key


@pytest.fixture(autouse=True)
def _pin_dns() -> None:
    """Resolve hosts for real. The client's own DNS pinning stays in force."""
    return None


@pytest.fixture
async def client():
    instance = DiscoverSwissClient(load_settings(require_key=True))
    try:
        yield instance
    finally:
        await instance.aclose()


def _measure(name: str, value: object, floor: object) -> None:
    """Print the measured value, so ``-rA`` puts it into the gate output."""
    print(f"CANARY {name}: measured={value} floor={floor}")


def _assert_live(response: object) -> None:
    """A degraded answer is not a measurement. Say which state it was."""
    degraded = getattr(response, "degraded", None)
    assert degraded is None, (
        f"degraded={degraded!r}, provenance={getattr(response, 'provenance', None)!r}, "
        f"hint={getattr(response, 'hint', None)!r} — the canary measured nothing"
    )


# ---------------------------------------------------------------------------
# Recall canaries — the probe's ground truth, halved
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("query", "floor"),
    [
        ("Landesmuseum", 20),  # 53 on 2026-09-17
        ("Grindelwald", 15),  # 37
        ("Wanderung", 200),  # 529
    ],
)
async def test_search_recall(client: DiscoverSwissClient, query: str, floor: int) -> None:
    response = await search_impl(client, SearchInput(query=query))
    _assert_live(response)
    _measure(f"search({query!r}).upstream_count", response.upstream_count, floor)
    assert response.upstream_count is not None
    assert response.upstream_count >= floor


async def test_accommodation_near_interlaken_is_national_scope(
    client: DiscoverSwissClient,
) -> None:
    # No radius: distance only ranks, so the count is every lodging in the
    # index (3'093 hotels by leafType, 5'275 businesses by list).
    response = await find_accommodation_impl(client, FindAccommodationInput(near=INTERLAKEN))
    _assert_live(response)
    _measure("find_accommodation(near Interlaken).upstream_count", response.upstream_count, 2000)
    assert response.upstream_count is not None
    assert response.upstream_count >= 2000


async def test_accommodation_within_5_km_of_interlaken(client: DiscoverSwissClient) -> None:
    response = await find_accommodation_impl(
        client, FindAccommodationInput(near=INTERLAKEN, radius_km=5)
    )
    _assert_live(response)
    _measure(
        "find_accommodation(near Interlaken, 5 km).upstream_count", response.upstream_count, 40
    )
    assert response.upstream_count is not None
    assert response.upstream_count >= 40  # 83 on 2026-09-17


async def test_find_tours_all(client: DiscoverSwissClient) -> None:
    response = await find_tours_impl(client, FindToursInput())
    _assert_live(response)
    _measure("find_tours().upstream_count", response.upstream_count, 100)
    assert response.upstream_count is not None
    assert response.upstream_count >= 100  # 223


async def test_find_tours_region_glarnerland(client: DiscoverSwissClient) -> None:
    response = await find_tours_impl(client, FindToursInput(region="Glarnerland"))
    _assert_live(response)
    assert response.area is not None and response.area.identifier is not None, (
        f"area not resolved: {response.area!r}, hint={response.hint!r}"
    )
    _measure("find_tours(region='Glarnerland').upstream_count", response.upstream_count, 50)
    assert response.upstream_count is not None
    assert response.upstream_count >= 50  # 117 with containedInPlace=[ds_glarnerland]


async def test_find_tours_length_filter(client: DiscoverSwissClient) -> None:
    response = await find_tours_impl(client, FindToursInput(length_km_max=10))
    _assert_live(response)
    _measure("find_tours(length_km_max=10).upstream_count", response.upstream_count, 10)
    assert response.upstream_count is not None
    assert response.upstream_count >= 10  # 29 with `length le 10000`


@pytest.mark.parametrize(
    ("radius_km", "floor"),
    [
        (100.0, 30),  # 73 webcams in the index, all in Eastern Switzerland
        (25.0, 8),  # 17 on 2026-09-17
    ],
)
async def test_webcams_near_st_gallen(
    client: DiscoverSwissClient, radius_km: float, floor: int
) -> None:
    response = await webcams_near_impl(
        client, WebcamsNearInput(near=ST_GALLEN, radius_km=radius_km)
    )
    _assert_live(response)
    _measure(
        f"webcams_near(St. Gallen, {radius_km:g} km).upstream_count",
        response.upstream_count,
        floor,
    )
    assert response.upstream_count is not None
    assert response.upstream_count >= floor


async def test_explore_area_whole_index(client: DiscoverSwissClient) -> None:
    response = await explore_area_impl(client, ExploreAreaInput())
    _assert_live(response)
    _measure("explore_area().total", response.total, 15000)
    assert response.total is not None
    assert response.total >= 15000  # 20'817


async def test_zurich_tourismus_partner_scope(client: DiscoverSwissClient) -> None:
    """The datasource `zht-cms`, reached through search as `sourcePartner`.

    No tool exposes a provider filter, so this goes through the client's
    `search` — the same call path, project and headers every tool uses.
    """
    result = await client.search(
        {"sourcePartner": [ZURICH_TOURISMUS], "resultsPerPage": 1, "select": "identifier"}
    )
    _measure("search(sourcePartner=zht).count", result.count, 600)
    assert result.count is not None
    assert result.count >= 600  # 1'311 by facet


async def test_find_events_next_year(client: DiscoverSwissClient) -> None:
    today = _today()
    response = await find_events_impl(
        client, FindEventsInput(from_date=today, to_date=today + timedelta(days=365))
    )
    _assert_live(response)
    _measure("find_events(today..+365 d).upstream_count", response.upstream_count, 5)
    assert response.upstream_count is not None
    assert response.upstream_count >= 5  # 18 with the OData schedule filter


# ---------------------------------------------------------------------------
# Fidelity canaries — scope parameters and field names actually take effect
# ---------------------------------------------------------------------------


async def test_match_name_narrows_the_search(client: DiscoverSwissClient) -> None:
    """`searchFields=name` must reach upstream: fewer hits, but not none.

    If `match` stopped being sent, both counts would be equal (53 / 53); if
    the field name were wrong, `name` would answer 0. Probe: 53 vs. 7.
    """
    by_name = await search_impl(client, SearchInput(query="Landesmuseum", match="name"))
    everywhere = await search_impl(client, SearchInput(query="Landesmuseum", match="all"))
    _assert_live(by_name)
    _assert_live(everywhere)
    _measure(
        "search('Landesmuseum') name vs all",
        f"{by_name.upstream_count} < {everywhere.upstream_count}",
        ">= 3 and strictly less",
    )
    assert by_name.upstream_count is not None and everywhere.upstream_count is not None
    assert by_name.upstream_count >= 3
    assert by_name.upstream_count < everywhere.upstream_count


async def test_facet_odata_name_comes_back(client: DiscoverSwissClient) -> None:
    """`containedInPlace/id` is the name the API answers to.

    The filterPropertyName spelling `containedInPlace` is dropped without an
    error (PROBE_VERIFY 1). A key in the answer is the proof the name was right.
    """
    response = await explore_area_impl(client, ExploreAreaInput(facets=["containedInPlace/id"]))
    _assert_live(response)
    _measure(
        "explore_area(facet containedInPlace/id).facets", sorted(response.facets), "key present"
    )
    assert "containedInPlace/id" in response.facets
    assert response.facets["containedInPlace/id"], "facet present but empty"
    assert "containedInPlace/id" not in response.missing_facets


async def test_detail_description_is_plain_text(client: DiscoverSwissClient) -> None:
    """Landesmuseum: «Z&uuml;rcher Hauptbahnhof» upstream, «Zürcher Hauptbahnhof» here."""
    response = await get_details_impl(client, GetDetailsInput(identifier=LANDESMUSEUM_ID))
    _assert_live(response)
    assert response.detail is not None, f"no detail: hint={response.hint!r}"
    description = response.detail.get("description") or ""
    _measure(
        "get_details(Landesmuseum).description[:80]", description[:80], "Hauptbahnhof, no entity"
    )
    assert "Hauptbahnhof" in description
    assert not ENTITY.search(description), ENTITY.search(description)
    assert "<p" not in description and "<br" not in description


# ---------------------------------------------------------------------------
# Distance and filter canaries
# ---------------------------------------------------------------------------


async def test_nearest_hotel_to_interlaken_is_in_interlaken(client: DiscoverSwissClient) -> None:
    response = await find_accommodation_impl(client, FindAccommodationInput(near=INTERLAKEN))
    _assert_live(response)
    assert response.hits, f"no hit: hint={response.hint!r}"
    first = response.hits[0]
    _measure(
        "find_accommodation(near Interlaken).hits[0]",
        f"{first.name} / {first.locality}",
        "Interlaken",
    )
    assert first.locality == "Interlaken"


async def test_demo_event_is_filtered_and_counted(client: DiscoverSwissClient) -> None:
    """«Demo Event» is withheld and counted, not dropped silently.

    One page of 50 covers the whole event stock (21), so the counter sees the
    demo record wherever the ranking puts it. At 0 the test skips: either the
    record was removed upstream, or the filter stopped matching — the skip
    reason says to find out which.
    """
    response = await find_events_impl(client, FindEventsInput(page_size=50))
    _assert_live(response)
    _measure("find_events().excluded_test_objects", response.excluded_test_objects, 1)
    if response.excluded_test_objects == 0:
        pytest.skip(
            "excluded_test_objects == 0 — Demo-Event entfernt? Check upstream for «Demo Event» "
            "before concluding the filter broke."
        )
    assert response.excluded_test_objects >= 1
    assert all("demo" not in (hit.name or "").lower() for hit in response.hits)
