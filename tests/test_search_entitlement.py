"""Search entitlement: an Open key never reaches ``/search``.

discover.swiss stated in writing (recorded 2026-10-05) that the Infocenter
Open product may not use search; the endpoint answering 200 to an Open key is
a fault on their side. These tests hold the consequence: without
``DISCOVER_SWISS_SEARCH_ENTITLED=true`` not a single request goes to
``/search`` — not even one to find out — and every tool still answers, from
the lists or degraded, never with a silent empty result.
"""

from __future__ import annotations

import copy
from typing import Any

import httpx
import pytest
from conftest import json_response, probe_fixture

from discover_swiss_mcp.client import DiscoverSwissClient, SearchUnavailableError
from discover_swiss_mcp.config import ConfigError, load_settings
from discover_swiss_mcp.tools import (
    FALLBACK_HINT,
    FindToursInput,
    GeoPoint,
    SearchInput,
    find_tours_impl,
    search_impl,
    source_status_impl,
)

ZURICH_HB = GeoPoint(lat=47.3779, lon=8.5403)
LIST_ENDPOINTS = (
    "places",
    "civicStructures",
    "foodEstablishments",
    "localbusinesses",
    "lodgingbusinesses",
)


@pytest.fixture
def not_entitled(monkeypatch) -> None:
    """The default configuration: conftest turns search on for the rest of the suite."""
    monkeypatch.delenv("DISCOVER_SWISS_SEARCH_ENTITLED", raising=False)


@pytest.fixture
async def open_client(not_entitled):
    instance = DiscoverSwissClient(load_settings())
    try:
        yield instance
    finally:
        await instance.aclose()


def _museum_row() -> dict[str, Any]:
    row = copy.deepcopy(probe_fixture("probe_open_out", "select_row_civicStructures.json"))
    row.update(
        identifier="civ_wow",
        name="WOW Museum",
        geo={"latitude": 47.375022, "longitude": 8.54033},
        additionalType="Museum",
    )
    return row


def test_search_is_off_by_default(not_entitled) -> None:
    settings = load_settings()
    assert settings.search_entitled is False
    assert settings.safe_summary()["search"] == "disabled"


def test_search_entitlement_is_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_SEARCH_ENTITLED", "TRUE")
    assert load_settings().search_entitled is True


def test_search_entitlement_typo_is_a_config_error(monkeypatch) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_SEARCH_ENTITLED", "yes")
    with pytest.raises(ConfigError):
        load_settings()


def test_legacy_confirmation_date_is_refused(monkeypatch) -> None:
    # A date here used to mean «Open may search». It no longer can.
    monkeypatch.setenv("DISCOVER_SWISS_ENTITLEMENT_CONFIRMED", "2026-10-01")
    with pytest.raises(ConfigError, match="no longer supported"):
        load_settings()


def test_legacy_pending_value_is_ignored(monkeypatch, not_entitled) -> None:
    # The old `.env.example` shipped `pending`; it claimed nothing.
    monkeypatch.setenv("DISCOVER_SWISS_ENTITLEMENT_CONFIRMED", "pending")
    assert load_settings().search_entitled is False


async def test_client_never_calls_search_without_entitlement(api_mock, open_client) -> None:
    search_route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": []})
    )
    assert open_client.search_available is False
    with pytest.raises(SearchUnavailableError, match="does not include /search"):
        await open_client.search({"searchText": "Landesmuseum"})
    assert search_route.call_count == 0


async def test_search_answers_from_the_lists_without_touching_search(api_mock, open_client) -> None:
    search_route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": []})
    )
    routes = {
        endpoint: api_mock.get(f"/{endpoint}").mock(
            return_value=json_response(
                {
                    "count": 1 if endpoint == "civicStructures" else 0,
                    "data": [_museum_row()] if endpoint == "civicStructures" else [],
                    "hasNextPage": False,
                }
            )
        )
        for endpoint in LIST_ENDPOINTS
    }

    result = await search_impl(
        open_client, SearchInput(types=["Museum"], near=ZURICH_HB, radius_km=2)
    )

    assert search_route.call_count == 0
    assert routes["civicStructures"].call_count == 1
    assert result.provenance == "list_fallback"
    assert result.degraded == "search_unavailable"
    assert result.hint is not None and result.hint.startswith(FALLBACK_HINT)
    assert [hit.identifier for hit in result.hits] == ["civ_wow"]


async def test_search_only_tool_answers_degraded_without_touching_search(
    api_mock, open_client
) -> None:
    search_route = api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": []})
    )
    result = await find_tours_impl(open_client, FindToursInput(near=ZURICH_HB))
    assert search_route.call_count == 0
    assert result.degraded == "search_unavailable"
    assert result.hint and "absence cannot be inferred" in result.hint


async def test_status_names_the_missing_entitlement(api_mock, open_client) -> None:
    api_mock.get("/status").mock(return_value=httpx.Response(204))
    search_route = api_mock.post("/search").mock(
        return_value=json_response({"count": 20817, "values": [], "facets": {}})
    )

    status = await source_status_impl(open_client)

    assert search_route.call_count == 0
    assert status.reachable is True
    assert status.search_available is False
    assert status.degraded == "search_unavailable"
    assert status.hint and "never calls it" in status.hint
    assert status.entitlement_note.startswith("Search disabled")
    assert status.index_total is None
