"""HTML to text, and the detail budget.

Both fixtures are recorded live responses, not hand-written samples: the
Landesmuseum description is the actual HTML the index serves, and Hotel Du Nord
is the 78 KB object that made trimming a requirement rather than a nicety.
"""

from __future__ import annotations

from conftest import probe_fixture

from discover_swiss_mcp.transform import (
    DETAIL_TARGET_BYTES,
    MAX_AMENITIES,
    MAX_LINKS,
    MAX_PHOTOS,
    html_to_text,
    json_size,
    localized,
    trim_detail,
)


def landesmuseum() -> dict:
    return probe_fixture("probe_detail_out", "detail_civic_landesmuseum.json")


def hotel() -> dict:
    return probe_fixture("probe_detail_out", "detail_hotel_interlaken.json")


# --------------------------------------------------------------------------
# html_to_text
# --------------------------------------------------------------------------


def test_the_landesmuseum_description_arrives_as_readable_text() -> None:
    text = html_to_text(landesmuseum()["description"])
    assert "Zürcher Hauptbahnhof" in text
    assert "&uuml;" not in text
    assert "&nbsp;" not in text
    assert "<p>" not in text
    assert "<" not in text


def test_a_double_break_stays_a_paragraph_break() -> None:
    text = html_to_text(landesmuseum()["description"])
    assert "\n\n" in text
    assert "\n\n\n" not in text


def test_the_fee_table_becomes_one_line_per_row() -> None:
    """«Erwachsene CHF 13» — the price belongs on the line of what it buys."""
    text = html_to_text(landesmuseum()["fees"])
    assert "Erwachsene CHF 13" in text
    assert "Ermässigt CHF 10" in text
    assert "Kinder (bis 16 Jahre) gratis" in text
    assert "<table>" not in text


def test_inline_tags_do_not_split_a_word() -> None:
    assert html_to_text("Ver<b>bind</b>ung") == "Verbindung"


def test_entities_are_resolved_after_the_tags_are_gone() -> None:
    assert html_to_text("a &lt;b&gt; c") == "a <b> c"


def test_empty_and_non_string_input_is_none() -> None:
    assert html_to_text(None) is None
    assert html_to_text("") is None
    assert html_to_text("   ") is None
    assert html_to_text("<p></p>") is None
    assert html_to_text(42) is None


def test_localized_picks_the_requested_language() -> None:
    profile = {"de": "Aktivrollstuhl", "en": "Active wheelchair", "fr": "Fauteuil roulant actif"}
    assert localized(profile, "en") == "Active wheelchair"
    assert localized(profile, "de") == "Aktivrollstuhl"
    assert localized(profile, "it") == "Aktivrollstuhl"  # falls back to de
    assert localized("plain", "en") == "plain"


# --------------------------------------------------------------------------
# trim_detail
# --------------------------------------------------------------------------


def test_the_78_kb_hotel_fits_in_the_budget() -> None:
    raw = hotel()
    trimmed = trim_detail(raw)
    assert json_size(raw) > 70_000
    assert json_size(trimmed) <= DETAIL_TARGET_BYTES


def test_the_museum_fits_too() -> None:
    assert json_size(trim_detail(landesmuseum())) <= DETAIL_TARGET_BYTES


def test_the_hotel_keeps_what_a_guest_asks_about() -> None:
    trimmed = trim_detail(hotel())
    assert trimmed["name"] == "Hotel Du Nord"
    assert trimmed["starRating"] == {"ratingValue": 4.0, "garni": True, "superior": False}
    assert trimmed["checkinTime"] == "15:00:00"
    assert trimmed["numberOfBeds"] == 113
    assert trimmed["address"]["addressLocality"] == "Interlaken"
    assert trimmed["geo"]["latitude"] == 46.688237
    assert trimmed["license"] == "CC BY"


def test_the_caps_hold() -> None:
    raw = hotel()
    trimmed = trim_detail(raw)
    assert len(raw["photo"]) == 40
    assert len(trimmed["photo"]) == MAX_PHOTOS
    assert len(raw["amenityFeature"]) == 81
    assert len(trimmed["amenityFeature"]) == MAX_AMENITIES
    assert all(isinstance(entry, str) for entry in trimmed["amenityFeature"])
    assert len(trimmed["link"]) <= MAX_LINKS


def test_the_governance_chain_and_the_rest_are_dropped() -> None:
    trimmed = trim_detail(hotel())
    for dropped in (
        "dataGovernance",
        "additionalProperty",
        "category",
        "autoTranslatedData",
        "paymentAccepted",
        "tag",
    ):
        assert dropped not in trimmed


def test_the_museum_keeps_its_own_fields() -> None:
    trimmed = trim_detail(landesmuseum())
    assert trimmed["zurichcard"] is True
    assert trimmed["zurichcardDescription"] == "Freier Eintritt"
    assert "Erwachsene CHF 13" in trimmed["fees"]
    assert len(trimmed["openingHoursSpecification"]) == 6
    assert trimmed["containedInPlace"][:2] == ["Schweiz", "Zürich"]
    assert trimmed["image"].startswith("https://")


def test_accessibility_keeps_three_fields_and_resolves_the_language() -> None:
    entries = trim_detail(landesmuseum(), lang="en")["accessibility"]
    assert entries
    assert set(entries[0]) == {"ratingProfileName", "grade", "conformance"}
    assert entries[0]["ratingProfileName"] == "Active wheelchair"


def test_empty_values_do_not_cost_bytes() -> None:
    trimmed = trim_detail({"identifier": "x", "name": "y", "telephone": None, "photo": []})
    assert trimmed == {"identifier": "x", "name": "y"}


def test_a_non_object_trims_to_nothing() -> None:
    assert trim_detail(None) == {}
