"""Scope defaults are sent, not inherited (audit FID-001), and area lookups
say what they compared (FID-L02).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from conftest import json_response

from discover_swiss_mcp.tools import (
    FindToursInput,
    GetDetailsInput,
    find_tours_impl,
    get_details_impl,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import default_matrix  # noqa: E402


def test_every_spec_parameter_has_a_decision() -> None:
    """A parameter the spec gains fails here until someone decides about it."""
    assert default_matrix.undecided() == {}
    assert default_matrix.stale_decisions() == {}


def test_the_published_matrix_is_current() -> None:
    assert default_matrix.OUT.read_text(encoding="utf-8") == default_matrix.render()


# ---------------------------------------------------------------------------
# On the wire
# ---------------------------------------------------------------------------


def _area_facet(values: list[tuple[str, str, int]]) -> dict:
    return {
        "count": 345,
        "values": [],
        "facets": {
            "containedInPlace/id": {
                "values": [{"value": v, "name": n, "count": c} for v, n, c in values],
            }
        },
    }


async def test_the_area_lookup_sends_its_facet_ordering(api_mock, client) -> None:
    route = api_mock.post("/search").mock(
        return_value=json_response(_area_facet([("ds_glarnerland", "Glarnerland", 345)]))
    )
    await client.resolve_area("Glarnerland")
    body = json.loads(route.calls[0].request.content)
    (facet,) = body["facets"]
    assert facet == {
        "name": "containedInPlace/id",
        "count": 30,
        "orderBy": "count",
        "orderDirection": "desc",
    }


async def test_a_truncated_area_comparison_says_so(api_mock, client) -> None:
    values = [(f"a{i}", f"Area {i}", 1000 - i) for i in range(30)]
    api_mock.post("/search").mock(return_value=json_response(_area_facet(values)))
    lookup = await client.resolve_area("Kleinstgemeinde")
    assert lookup.identifier is None
    assert "Only the 30 areas" in (lookup.hint or "")


async def test_an_untruncated_comparison_does_not_claim_truncation(api_mock, client) -> None:
    """The counter-check: fewer than 30 values means everything was compared."""
    api_mock.post("/search").mock(return_value=json_response(_area_facet([("a1", "Area 1", 10)])))
    lookup = await client.resolve_area("Kleinstgemeinde")
    assert "Only the 30 areas" not in (lookup.hint or "")


async def test_a_missing_area_facet_is_not_no_area(api_mock, client) -> None:
    """Without the facet, «no area is named X» would be a claim about unseen data."""
    api_mock.post("/search").mock(return_value=json_response({"count": 345, "values": []}))
    response = await find_tours_impl(client, FindToursInput(region="Glarnerland"))
    assert response.degraded == "upstream_shape_changed"
    assert "No area is named" not in (response.hint or "")


async def test_the_detail_call_pins_include_all_photos(api_mock, client) -> None:
    route = api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response({"identifier": "civ_px9-s28_bggg", "name": "x"})
    )
    await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    params = route.calls[0].request.url.params
    assert params["includeAllPhotos"] == "false"
    assert params["project"] == "dsod-content"


@pytest.mark.parametrize("lang", ["de", "fr", "it", "en"])
async def test_accept_language_is_always_sent(api_mock, client, lang: str) -> None:
    """The default would be de-CH: French callers would get German names silently."""
    route = api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response({"identifier": "civ_px9-s28_bggg", "name": "x"})
    )
    await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg", lang=lang))
    assert route.calls[0].request.headers["accept-language"] == lang
