"""The licence gate, attribution and the test-object filter.

The six licence strings below are the ones the probe found on page one of the
content endpoints. Three of them must never reach a caller.
"""

from __future__ import annotations

import pytest
from conftest import probe_fixture

from discover_swiss_mcp.licenses import (
    ALLOWED,
    attribution,
    is_allowed_license,
    is_no_derivatives,
    is_servable,
    is_test_object,
    license_of,
    normalize_license,
    screen,
)

# What the probe measured, endpoint by endpoint.
SERVED = ["CC BY", "CC BY-SA", "CC BY-ND"]
WITHHELD = ["C-All-Rights-Reserved", None, "CC BY-NC-SA"]


@pytest.mark.parametrize("value", SERVED)
def test_the_three_open_licences_are_served(value: str) -> None:
    assert is_allowed_license(value) is True


@pytest.mark.parametrize("value", WITHHELD)
def test_the_three_closed_licences_are_withheld(value: str | None) -> None:
    assert is_allowed_license(value) is False


@pytest.mark.parametrize(
    "value",
    ["CC-BY", "cc by", "CC  BY-SA", " CC BY - SA ", "ccby".upper().replace("CCBY", "CC BY")],
)
def test_spelling_does_not_decide_the_licence(value: str) -> None:
    assert is_allowed_license(value) is True


def test_every_whitelisted_spelling_passes_its_own_gate() -> None:
    assert all(is_allowed_license(entry) for entry in ALLOWED)


def test_normalize_license_ignores_non_strings() -> None:
    assert normalize_license(None) == ""
    assert normalize_license(42) == ""


def test_nc_is_not_open_enough_to_pass() -> None:
    """Non-commercial is a restriction a downstream use cannot honour for the user."""
    for value in ("CC BY-NC", "CC BY-NC-SA", "CC BY-NC-ND"):
        assert is_allowed_license(value) is False


# --------------------------------------------------------------------------
# Where the licence comes from
# --------------------------------------------------------------------------


def test_detail_objects_use_their_root_licence() -> None:
    landesmuseum = probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")
    hotel = probe_fixture("probe_detail_out", "detail_hotel_interlaken.json")
    assert license_of(landesmuseum) == "CC BY-SA"
    assert license_of(hotel) == "CC BY"
    assert is_servable(landesmuseum) and is_servable(hotel)


def test_a_search_hit_without_a_root_licence_derives_it_from_its_provider() -> None:
    """`IndexResponse` has no `license` field, so `/search` can never send one.

    The provider's own origin decides — not the first one in the list, which
    for the Landesmuseum is Guidle with all rights reserved.
    """
    landesmuseum = probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")
    as_search_hit = {k: v for k, v in landesmuseum.items() if k != "license"}
    assert license_of(as_search_hit) == "CC BY-SA"

    origins = as_search_hit["dataGovernance"]["origin"]
    assert any(o.get("license") == "C-All-Rights-Reserved" for o in origins)


def test_an_object_whose_provider_has_no_origin_is_not_guessed_open() -> None:
    obj = {
        "name": "Hotelgruppe",
        "dataGovernance": {
            "provider": {"acronym": "hs", "name": "HotellerieSuisse"},
            "origin": [{"datasource": "osm", "license": "ODbL"}],
        },
    }
    assert license_of(obj) is None
    assert is_servable(obj) is False


def test_an_object_without_any_licence_is_withheld() -> None:
    assert is_servable({"name": "Hotelkette", "license": None}) is False
    assert is_servable({"name": "Hotelkette"}) is False


# --------------------------------------------------------------------------
# ND and attribution
# --------------------------------------------------------------------------


def test_nd_is_flagged_so_details_quote_rather_than_reword() -> None:
    assert is_no_derivatives({"license": "CC BY-ND"}) is True
    assert is_no_derivatives({"license": "CC BY-SA"}) is False
    assert is_no_derivatives({"license": "CC BY"}) is False


def test_attribution_is_built_from_the_object_itself() -> None:
    landesmuseum = probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")
    credit = attribution(landesmuseum)
    assert credit.provider == "Zürich Tourismus"
    assert credit.license == "CC BY-SA"
    assert credit.copyright_notice == "Zürich Tourismus www.zuerich.com"
    # The first WebHomepage link, not the ginto accessibility link behind it.
    assert credit.source_url == "https://www.landesmuseum.ch"


def test_attribution_falls_back_to_url_then_to_unknown() -> None:
    hotel = probe_fixture("probe_detail_out", "detail_hotel_interlaken.json")
    credit = attribution(hotel)
    assert credit.provider == "HotellerieSuisse"
    assert credit.copyright_notice is None
    assert credit.source_url == "http://www.hotel-dunord.ch"

    bare = attribution({"license": "CC BY", "url": "https://example.org"})
    assert bare.provider == "unknown"
    assert bare.source_url == "https://example.org"


# --------------------------------------------------------------------------
# Test objects in the production index
# --------------------------------------------------------------------------


DEMO_EVENT = {
    "identifier": "eve_s9t_dshjrcer-tfsb-essd-rirq-hugidebuvjge",
    "type": "Event",
    "name": "Demo Event",
    "license": "CC BY-SA",
    "address": {"streetAddress": "Strasse 1", "postalCode": "PLZ", "addressLocality": "Ort"},
    "organizer": {"email": "mail@example.ch"},
}


def test_the_demo_event_is_recognised() -> None:
    assert is_test_object(DEMO_EVENT) is True


@pytest.mark.parametrize(
    "obj",
    [
        {"name": "Test Openair"},
        {"name": "Beispiel-Führung"},
        {"name": "Muster Museum"},
        {"name": "placeholder entry"},
        {"name": "Echtes Fest", "address": {"streetAddress": "Musterstrasse 1"}},
        {"name": "Echtes Fest", "address": {"postalCode": "PLZ"}},
        {"name": "Echtes Fest", "address": {"addressLocality": "Ort"}},
        {"name": "Echtes Fest", "address": {"email": "info@example.com"}},
        {"name": "Echtes Fest", "email": "info@example.ch"},
    ],
)
def test_every_placeholder_marker_counts(obj: dict) -> None:
    assert is_test_object(obj) is True


@pytest.mark.parametrize(
    "name",
    [
        "Attestor Bar",
        "Demokratie-Forum",
        "Musterplatz-Konzert",
        "Protestmarsch",
        "Testlauf Openair",
    ],
)
def test_a_word_boundary_keeps_real_names_in(name: str) -> None:
    """«Demo» inside «Demokratie» is not a test record.

    The rule cuts both ways, and the last case names the cost: a German
    compound such as «Testlauf» is not caught either. Widening the pattern to
    prefixes would take «Demokratie-Forum» and «Protestmarsch» with it, which
    is the worse error — a real event withheld reads as no event at all, while
    a missed placeholder is still visible as the nonsense it is.
    """
    assert is_test_object({"name": name}) is False


def test_screen_counts_what_it_drops() -> None:
    result = screen(
        [
            {"name": "Landesmuseum", "license": "CC BY-SA"},
            {"name": "Guidle-Event", "license": "C-All-Rights-Reserved"},
            {"name": "Hotelkette", "license": None},
            DEMO_EVENT,
        ]
    )
    assert [obj["name"] for obj in result.kept] == ["Landesmuseum"]
    assert result.excluded_by_license == 2
    assert result.excluded_test_objects == 1


def test_screen_counts_each_object_once() -> None:
    """A closed-licence placeholder is excluded by licence, not by both gates."""
    closed_demo = {**DEMO_EVENT, "license": "C-All-Rights-Reserved"}
    result = screen([closed_demo])
    assert result.excluded_by_license == 1
    assert result.excluded_test_objects == 0
    assert result.kept == []
