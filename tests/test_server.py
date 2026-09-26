"""The protocol layer: what a client sees of the eight tools.

Two things are only true at this layer and are tested here rather than in
`test_tools.py`: the annotations and descriptions a model reads, and the path
from a tool call through the lifespan's shared client — including the missing
key, which must be a named error and not ten minutes of `search_unavailable`.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path

import pytest
from conftest import json_response, probe_fixture
from mcp import Client

from discover_swiss_mcp.server import MCP_PROTOCOL_VERSION, mcp

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "docs" / "tool-hashes.json"

# The sentences the P2 and P3 briefs fix verbatim. The descriptions may add to
# them, never reword them.
#
# Three were reworded after the audit of 2026-09-26 (FID-005), against the P4
# session rule that no description explains or apologises for an empty result:
# `search` states the query syntax measured by `probes/probe_query_syntax.py`
# on 2026-09-26 (PROBE_QUERY) and leaves open only what the probe could not
# settle (compound parts); `find_events` and `webcams_near` lost the sentence about what to
# do when they return nothing — that sentence lives in their `hint`.
VERBATIM = {
    "search": (
        "Full-text and geo search over discover.swiss open tourism data (~20k objects: hotels "
        "nationwide; museums, restaurants, shops, tours, webcams, ski resorts for Zurich, "
        "Eastern Switzerland, Liechtenstein, Engadin). `query` is matched in name AND "
        "descriptions by default (`match='all'`), so a hit count includes objects that merely "
        "mention the term; use `match='name'` to match names only. Query syntax (measured): "
        "whole words, case-insensitive; several words must all match. Not supported: prefixes "
        "or fragments ('Landesmus' finds nothing), wildcards (*, ?), fuzzy (~), AND/OR, "
        "exclusion with '-' — these return 0 or fewer hits, never an error; quotes change "
        "nothing. Send whole words; for alternatives run one search each. Whether part of a "
        "compound matches (museum in Landesmuseum) is not established. `near` ranks by distance "
        "from a coordinate; `locality` filters by the "
        "exact municipality name in the address. Rooms and meeting rooms are excluded unless "
        "requested via `types`. Every hit carries its own licence and attribution — cite the "
        "provider when you present it. Empty result: follow the `hint` before concluding "
        "anything."
    ),
    "get_details": (
        "Full details for one object by identifier: description, address, opening hours, fees, "
        "accessibility (Pro Infirmis profiles), amenities, star rating, check-in times, photos, "
        "links. Response is trimmed to ~8 KB. If `no_derivatives` is true the description is "
        "licensed CC BY-ND: quote it verbatim or summarise facts, do not rewrite it as your own "
        "text. Opening hours and prices are provider-maintained and can be outdated — say so "
        "when you present them (see `disclaimer`)."
    ),
    "find_events": (
        "Event coverage in this source is thin (about 20 objects, mostly Eastern Switzerland; "
        "Zurich events are not included because their provider is not open-licensed)."
    ),
    "webcams_near": (
        "73 webcams, all in Eastern Switzerland (St. Gallen, Thurgau, Toggenburg, Heidiland, "
        "Glarnerland, Appenzell). `live_url` opens the provider's live image; `snapshot_url` "
        "is a stored still and may be hours old."
    ),
    "explore_area": (
        "Overview of what exists in a region before searching: counts by object type, data "
        "owner, season, price range. Use it to decide which tool to call next and to avoid "
        "asking for things this source does not have. Counts are upstream counts before "
        "licence filtering."
    ),
    "source_status": (
        "Health and scope of this server. Call it first when another tool returned `degraded` "
        "or an unexpected empty result."
    ),
}

ALL_TOOLS = [
    "search",
    "get_details",
    "find_accommodation",
    "find_tours",
    "find_events",
    "webcams_near",
    "explore_area",
    "source_status",
]


def _tools() -> dict:
    return {tool.name: tool for tool in asyncio.run(mcp.list_tools())}


def _hash_script():
    """`scripts/gen_tool_hashes.py`, loaded by path: the test runs the same script CI runs."""
    spec = importlib.util.spec_from_file_location(
        "gen_tool_hashes", ROOT / "scripts" / "gen_tool_hashes.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ALL_TOOLS)
def test_every_tool_is_read_only_and_open_world(name: str) -> None:
    annotations = _tools()[name].annotations
    assert annotations.read_only_hint is True
    assert annotations.open_world_hint is True
    assert annotations.destructive_hint is False


@pytest.mark.parametrize("name", sorted(VERBATIM))
def test_fixed_descriptions_are_carried_verbatim(name: str) -> None:
    description = " ".join(_tools()[name].description.split())
    assert VERBATIM[name] in description


def test_accommodation_description_names_what_the_source_lacks() -> None:
    description = _tools()["find_accommodation"].description
    for fact in ("5'275", "HotellerieSuisse", "Pro Infirmis", "OK:GO", "NO availability"):
        assert fact in description


def test_no_description_apologises_for_an_empty_result() -> None:
    """mcp-data-fidelity rule 4: the hint explains an empty set, the description does not."""
    for tool in _tools().values():
        text = tool.description.lower()
        assert "no results" not in text
        assert "may return nothing" not in text


def test_every_tool_has_an_output_schema() -> None:
    assert all(tool.output_schema for tool in _tools().values())


def test_every_response_schema_carries_the_envelope() -> None:
    """Attribution and provenance travel in the response — for all eight tools."""
    for tool in _tools().values():
        properties = tool.output_schema["properties"]
        for field in ("source", "provenance", "retrieved_at", "source_freshness", "degraded"):
            assert field in properties, (tool.name, field)


# ---------------------------------------------------------------------------
# Tool hash snapshot (SEC-022)
# ---------------------------------------------------------------------------


def test_tool_hash_snapshot_matches() -> None:
    """An intended change is confirmed with `python scripts/gen_tool_hashes.py --write`."""
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    current = asyncio.run(_hash_script().current_hashes())
    assert snapshot["mcp_protocol_version"] == MCP_PROTOCOL_VERSION
    assert snapshot["tool_count"] == len(current)
    assert snapshot["tools"] == current


# ---------------------------------------------------------------------------
# Through the protocol
# ---------------------------------------------------------------------------


async def test_search_through_the_protocol(api_mock) -> None:
    page = probe_fixture("probe_out", "search_dsod-content_1.json")
    detail = probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")
    page["values"][0]["dataGovernance"] = detail["dataGovernance"]
    api_mock.post("/search").mock(return_value=json_response(page))

    async with Client(mcp) as client:
        result = await client.call_tool("search", {"params": {"query": "Landesmuseum"}})

    assert result.is_error is False
    payload = result.structured_content
    assert payload["upstream_count"] == 53
    assert payload["hits"][0]["attribution"]["provider"] == "Zürich Tourismus"
    # The four recorded hits without governance are withheld and counted.
    assert payload["excluded_by_license"] == 4


async def test_missing_key_is_a_named_error_not_a_withdrawn_search(monkeypatch, api_mock) -> None:
    monkeypatch.setenv("DISCOVER_SWISS_KEY", "")
    route = api_mock.post("/search").mock(return_value=json_response({}, status=401))

    async with Client(mcp) as client:
        result = await client.call_tool("search", {"params": {"query": "Rigi"}})

    assert result.is_error is True
    assert "DISCOVER_SWISS_KEY" in result.content[0].text
    assert route.call_count == 0


async def test_invalid_input_is_rejected_before_any_call(api_mock) -> None:
    route = api_mock.post("/search").mock(return_value=json_response({}))
    async with Client(mcp) as client:
        result = await client.call_tool("find_accommodation", {"params": {"stars_min": 3}})
    assert result.is_error is True
    assert route.call_count == 0


async def test_source_status_works_without_a_key(monkeypatch, api_mock) -> None:
    """The one tool that must answer when the key is missing — and say so."""
    monkeypatch.setenv("DISCOVER_SWISS_KEY", "")
    route = api_mock.get("/status").mock(return_value=json_response({}))

    async with Client(mcp) as client:
        result = await client.call_tool("source_status", {})

    assert result.is_error is False
    assert result.structured_content["api_key_configured"] is False
    assert route.call_count == 0


async def test_find_events_through_the_protocol(api_mock) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response({"count": 0, "values": [], "facets": {}})
    )
    async with Client(mcp) as client:
        result = await client.call_tool(
            "find_events", {"params": {"from_date": "2026-10-01", "to_date": "2026-10-31"}}
        )
    assert result.is_error is False
    assert result.structured_content["hint"].startswith("No open-licensed event in range.")
    body = json.loads(route.calls.last.request.read())
    assert "2026-10-31T23:59:59Z" in body["filters"][0]
