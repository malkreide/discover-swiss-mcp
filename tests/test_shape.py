"""A reader that does not recognise the answer says so (audit FID-006, FID-003).

The failure these tests exist for: the source reports 53 results, the root key
has moved, the reader finds an empty list and the tool answers «No hit» — which
a model cannot tell from a real empty result. Each refusal has its
counter-check: a genuine empty result must still read as empty.
"""

from __future__ import annotations

import pytest
from conftest import json_response

from discover_swiss_mcp import client as client_module
from discover_swiss_mcp.tools import (
    GetDetailsInput,
    SearchInput,
    get_details_impl,
    search_impl,
)

# ---------------------------------------------------------------------------
# /search envelope
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {"count": 53, "value": [{"identifier": "civ_x"}]},  # root key moved
        {"count": 53},  # rows gone, count still there
        {"count": 53, "values": {"identifier": "civ_x"}},  # object instead of list
        {"results": [], "total": 53},  # a different envelope altogether
        [{"identifier": "civ_x"}],  # no envelope at all
        {"count": 2, "values": [{"item": {"identifier": "a"}}, {"item": {"identifier": "b"}}]},
        {"count": 1, "values": ["civ_x"]},  # rows reduced to bare strings
    ],
)
async def test_an_unrecognised_search_answer_is_not_an_empty_result(
    api_mock, client, payload
) -> None:
    api_mock.post("/search").mock(return_value=json_response(payload))
    response = await search_impl(client, SearchInput(query="Landesmuseum"))
    assert response.degraded == "upstream_shape_changed"
    assert response.hits == []
    assert "not an empty result" in (response.hint or "")
    assert "No hit" not in (response.hint or "")


@pytest.mark.parametrize(
    "payload",
    [
        {"count": 0, "values": []},
        {"count": 0, "values": None},
        {"count": 0},
        {"count": 0, "facets": {}},
    ],
)
async def test_a_genuine_empty_search_result_stays_empty(api_mock, client, payload) -> None:
    """The counter-check: zero means zero, whichever form the source uses for it."""
    api_mock.post("/search").mock(return_value=json_response(payload))
    response = await search_impl(client, SearchInput(query="Xyzzy"))
    assert response.degraded is None
    assert response.upstream_count == 0
    assert response.hint and "No hit" in response.hint


async def test_facets_that_are_not_an_object_are_a_shape_error(api_mock, client) -> None:
    api_mock.post("/search").mock(
        return_value=json_response({"count": 1, "values": [], "facets": ["leafType"]})
    )
    with pytest.raises(client_module.UpstreamShapeError):
        await client.search({"searchText": "x"})


# ---------------------------------------------------------------------------
# List envelope
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {"count": 12, "hasNextPage": False},  # rows gone
        {"count": 12, "data": {"identifier": "x"}},
        {"items": [], "hasNextPage": False},
        {"count": 1, "data": [{"webcam": {"identifier": "x"}}]},  # rows nested one deeper
    ],
)
async def test_an_unrecognised_list_answer_raises(api_mock, client, payload) -> None:
    api_mock.get("/webcams").mock(return_value=json_response(payload))
    with pytest.raises(client_module.UpstreamShapeError):
        await client.list_endpoint("webcams")


async def test_rows_nested_one_deeper_are_not_read_as_licence_withheld(api_mock, client) -> None:
    """Re-verification of FID-006: every row fell to the licence filter as «withheld»."""
    api_mock.post("/search").mock(
        return_value=json_response(
            {"count": 2, "values": [{"doc": {"identifier": "a"}}, {"doc": {"identifier": "b"}}]}
        )
    )
    response = await search_impl(client, SearchInput(query="Landesmuseum"))
    assert response.degraded == "upstream_shape_changed"
    assert "licen" not in (response.hint or "").lower()


async def test_one_row_with_an_identifier_is_enough(api_mock, client) -> None:
    """The counter-check: a single odd row among good ones is not a changed shape."""
    api_mock.get("/webcams").mock(
        return_value=json_response(
            {"count": 2, "data": [{"identifier": "x"}, {"note": "odd"}], "hasNextPage": False}
        )
    )
    page = await client.list_endpoint("webcams")
    assert len(page.data) == 2


async def test_an_empty_list_page_stays_empty(api_mock, client) -> None:
    api_mock.get("/webcams").mock(
        return_value=json_response({"count": 0, "data": [], "hasNextPage": False})
    )
    page = await client.list_endpoint("webcams")
    assert page.data == []
    assert page.total == 0


# ---------------------------------------------------------------------------
# get_details: only a 404 or an invalid identifier is «unknown» (FID-003)
# ---------------------------------------------------------------------------


async def test_an_upstream_400_is_not_reported_as_unknown_identifier(api_mock, client) -> None:
    """A rejected request says nothing about whether the object exists."""
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(
        return_value=json_response({"message": "Bad Request"}, status=400)
    )
    with pytest.raises(client_module.UpstreamRejectedError) as excinfo:
        await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    assert not isinstance(excinfo.value, client_module.InvalidIdentifierError)


async def test_a_detail_that_is_not_an_object_is_a_shape_state(api_mock, client) -> None:
    api_mock.get("/vertices/civ_px9-s28_bggg").mock(return_value=json_response(["x"]))
    response = await get_details_impl(client, GetDetailsInput(identifier="civ_px9-s28_bggg"))
    assert response.degraded == "upstream_shape_changed"
    assert response.hint and "Unknown identifier" not in response.hint


async def test_an_invalid_identifier_and_a_404_are_unknown(api_mock, client) -> None:
    """The counter-check: the two cases that do mean «no such object»."""
    route = api_mock.get("/vertices/civ_gone").mock(
        return_value=json_response({"message": "Not found"}, status=404)
    )
    invalid = await get_details_impl(client, GetDetailsInput(identifier="../etc/passwd"))
    missing = await get_details_impl(client, GetDetailsInput(identifier="civ_gone"))
    assert "Unknown identifier" in (invalid.hint or "")
    assert "Unknown identifier" in (missing.hint or "")
    assert route.call_count == 1  # the invalid one never left the server


# ---------------------------------------------------------------------------
# get_details withholds test objects like every list tool (FID-L03)
# ---------------------------------------------------------------------------

DEMO_EVENT = {
    "identifier": "evt_demo",
    "name": "Demo Event",
    "type": "Event",
    "license": "CC BY-SA",
    "address": {"streetAddress": "Strasse 1", "postalCode": "PLZ", "addressLocality": "Ort"},
    "description": "<p>Platzhalter</p>",
}


async def test_a_test_object_is_withheld_and_counted_by_get_details(api_mock, client) -> None:
    api_mock.get("/vertices/evt_demo").mock(return_value=json_response(DEMO_EVENT))
    response = await get_details_impl(client, GetDetailsInput(identifier="evt_demo"))
    assert response.detail is None
    assert response.excluded_test_objects == 1
    assert "test record" in (response.hint or "")


async def test_a_real_object_named_like_a_test_is_not_withheld(api_mock, client) -> None:
    """The counter-check: an ordinary object passes through."""
    real = {**DEMO_EVENT, "identifier": "evt_real", "name": "Zürcher Jazznacht"}
    real["address"] = {
        "streetAddress": "Seefeldstrasse 5",
        "postalCode": "8008",
        "addressLocality": "Zürich",
    }
    api_mock.get("/vertices/evt_real").mock(return_value=json_response(real))
    response = await get_details_impl(client, GetDetailsInput(identifier="evt_real"))
    assert response.excluded_test_objects == 0
    assert response.detail is not None


# ---------------------------------------------------------------------------
# Query syntax the source does not understand (FID-005, PROBE_QUERY 2026-09-26)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query",
    [
        "Landesmus*",
        "Landesmuse?m",
        "Landesmusem~",
        "Landesmuseum AND Zürich",
        "Landesmuseum OR Kunsthaus",
        "Landesmuseum -Shop",
        '"Landesmuseum Zürich"',
    ],
)
async def test_an_empty_result_after_unsupported_syntax_names_the_syntax(
    api_mock, client, query
) -> None:
    api_mock.post("/search").mock(return_value=json_response({"count": 0, "values": []}))
    response = await search_impl(client, SearchInput(query=query))
    assert response.hint is not None
    assert response.hint.startswith("The query uses syntax the source does not understand")
    assert "No hit" in response.hint


@pytest.mark.parametrize("query", ["Landesmuseum", "Kloster St. Gallen", "Rhein-Falls", "Andorra"])
async def test_plain_words_get_the_ordinary_empty_hint(api_mock, client, query) -> None:
    """The counter-check: hyphenated words and names containing «and»/«or» are not operators."""
    api_mock.post("/search").mock(return_value=json_response({"count": 0, "values": []}))
    response = await search_impl(client, SearchInput(query=query))
    assert response.hint is not None
    assert response.hint.startswith("No hit")
