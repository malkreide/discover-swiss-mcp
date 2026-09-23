"""The protocol layer: what a client sees of the four P2 tools.

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

# The sentences the P2 brief fixes verbatim. The descriptions may add to them,
# never reword them.
VERBATIM = {
    "search": (
        "Full-text and geo search over discover.swiss open tourism data (~20k objects: hotels "
        "nationwide; museums, restaurants, shops, tours, webcams, ski resorts for Zurich, "
        "Eastern Switzerland, Liechtenstein, Engadin). `query` matches whole words in name AND "
        "descriptions by default (`match='all'`), so a hit count includes objects that merely "
        "mention the term; use `match='name'` for exact lookups. Compounds are not found by "
        "their parts. `near` ranks by distance from a coordinate; `locality` filters by the "
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
}


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


@pytest.mark.parametrize("name", ["search", "get_details", "find_accommodation", "find_tours"])
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
