"""Turning source records into something a model can actually read.

Two problems, both measured rather than assumed:

1. **Descriptions are HTML with entities.** The Landesmuseum description
   arrives as ``<p>Das Landesmuseum gleich beim Z&uuml;rcher Hauptbahnhof …``
   and the admission prices as an HTML ``<table>``. Passed through unchanged, a
   model either reads ``&uuml;`` aloud or quietly invents the encoding away.
2. **A single hotel weighs 78 KB.** Hotel Du Nord carries 40 photos, 81 amenity
   features and a data-governance chain per origin. Detail is a filter, not a
   pass-through; :func:`trim_detail` keeps the fields a guest question actually
   needs and drops the rest, aiming at ≤ 8 KB of JSON.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

# Target size for one trimmed detail object, serialised as UTF-8 JSON. Not a
# hard cap enforced by truncation — a silently cut object is worse than a large
# one — but the number the field budget below is measured against.
DETAIL_TARGET_BYTES = 8 * 1024

MAX_LINKS = 5
MAX_PHOTOS = 3
MAX_AMENITIES = 30

# Only *opening* structural tags produce a break, and closing ones produce
# nothing. Breaking on both would turn every `</tr><tr>` into a blank line, so a
# four-row price table would arrive twice as tall as it is — and the same rule
# then cannot tell that apart from a real paragraph break.
_PARAGRAPH_TAGS = re.compile(r"<\s*(?:p|div|h[1-6])\b[^>]*>", re.IGNORECASE)
_LINE_TAGS = re.compile(r"<\s*(?:br|li|tr|table|thead|tbody|ul|ol)\b[^>]*/?>", re.IGNORECASE)
# A table cell boundary is a column break, not a line break: «Erwachsene» and
# «CHF 13» belong on one line, which is what makes a price list readable.
_CELL_TAGS = re.compile(r"</\s*(?:td|th)\s*>", re.IGNORECASE)
_ANY_TAG = re.compile(r"<[^>]*>")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_TRAILING_SPACE = re.compile(r"[ \t]+\n")


def html_to_text(value: Any) -> str | None:
    """Resolve entities, turn block tags into line breaks, drop the rest.

    Returns ``None`` for anything that is not a non-empty string, so a caller
    can keep using ``or``-chains without a special case for ``None``.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    text = _CELL_TAGS.sub(" ", value)
    text = _PARAGRAPH_TAGS.sub("\n\n", text)
    text = _LINE_TAGS.sub("\n", text)
    text = _ANY_TAG.sub("", text)
    # After the tags, not before: an entity may itself encode a `<`, and
    # unescaping first would hand the tag stripper input the source never sent.
    text = html.unescape(text)
    # `&nbsp;` became U+00A0, which is not whitespace to `str.split()`.
    text = text.replace(" ", " ")

    lines = [" ".join(line.split()) for line in text.split("\n")]
    text = "\n".join(lines)
    text = _TRAILING_SPACE.sub("\n", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)
    return text.strip() or None


def localized(value: Any, lang: str = "de") -> Any:
    """Pick one language out of a ``{"de": …, "en": …}`` map.

    The index carries these maps in ``accessibility``; anything that is not
    such a map is returned unchanged.
    """
    if not isinstance(value, dict):
        return value
    if not value or not all(isinstance(key, str) and len(key) == 2 for key in value):
        return value
    for candidate in (lang, lang.split("-")[0], "de", "en"):
        if candidate in value:
            return value[candidate]
    return next(iter(value.values()))


def _accessibility(value: Any, lang: str) -> list[dict[str, Any]]:
    """Profile name, grade and conformance — the three fields a guest asks about."""
    if not isinstance(value, list):
        return []
    entries: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = {
            "ratingProfileName": localized(item.get("ratingProfileName"), lang),
            "grade": item.get("grade"),
            "conformance": item.get("conformance"),
        }
        if entry["ratingProfileName"] is not None:
            entries.append(entry)
    return entries


def _amenity_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name.strip() and name not in names:
                names.append(name.strip())
        if len(names) >= MAX_AMENITIES:
            break
    return names


def _links(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    links: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict) or not item.get("url"):
            continue
        links.append({k: item[k] for k in ("url", "type", "title", "inLanguage") if item.get(k)})
        if len(links) >= MAX_LINKS:
            break
    return links


def _photo_urls(value: Any, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    urls: list[str] = []
    for item in value:
        if isinstance(item, dict):
            url = item.get("contentUrl")
            if isinstance(url, str) and url and url not in urls:
                urls.append(url)
        if len(urls) >= limit:
            break
    return urls


def _star_rating(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    kept = {k: value[k] for k in ("ratingValue", "garni", "superior") if k in value}
    return kept or None


def _contained_in_place_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name.strip() and name not in names:
                names.append(name.strip())
    return names


def trim_detail(obj: dict[str, Any], lang: str = "de") -> dict[str, Any]:
    """Reduce one ``/vertices/{id}`` record to what a guest question needs.

    Kept: identity and type, the text fields as text, address, geo and contact,
    up to five links, opening hours, fees, Zurich Card, accessibility, up to 30
    amenity names, star rating and room counts, check-in/out, one image and
    three photos, and the licence fields that attribution is built from.
    Everything else — ``dataGovernance`` chains, 40 photos, 81 amenity objects,
    ``additionalProperty``, ``category``, ``osm_id``, ``autoTranslatedData`` —
    is dropped.

    Empty values are dropped too: ``"telephone": null`` costs bytes and tells
    the model nothing that its absence does not.
    """
    if not isinstance(obj, dict):
        return {}

    image = obj.get("image")
    image_url = image.get("contentUrl") if isinstance(image, dict) else None

    trimmed: dict[str, Any] = {
        "identifier": obj.get("identifier"),
        "name": obj.get("name"),
        "type": obj.get("type"),
        "additionalType": obj.get("additionalType"),
        "description": html_to_text(obj.get("description")),
        "disambiguatingDescription": html_to_text(obj.get("disambiguatingDescription")),
        "address": obj.get("address") if isinstance(obj.get("address"), dict) else None,
        "geo": obj.get("geo") if isinstance(obj.get("geo"), dict) else None,
        "telephone": obj.get("telephone"),
        "url": obj.get("url"),
        "link": _links(obj.get("link")),
        "openingHoursSpecification": obj.get("openingHoursSpecification"),
        "openingHours": html_to_text(obj.get("openingHours")),
        "fees": html_to_text(obj.get("fees")),
        "zurichcard": obj.get("zurichcard"),
        "zurichcardDescription": html_to_text(obj.get("zurichcardDescription")),
        "accessibility": _accessibility(obj.get("accessibility"), lang),
        "amenityFeature": _amenity_names(obj.get("amenityFeature")),
        "starRating": _star_rating(obj.get("starRating")),
        "checkinTime": obj.get("checkinTime"),
        "checkoutTime": obj.get("checkoutTime"),
        "numberOfRooms": obj.get("numberOfRooms"),
        "numberOfBeds": obj.get("numberOfBeds"),
        "image": image_url,
        "photo": _photo_urls(obj.get("photo"), MAX_PHOTOS),
        "lastModified": obj.get("lastModified"),
        "license": obj.get("license"),
        "copyrightNotice": obj.get("copyrightNotice"),
        "containedInPlace": _contained_in_place_names(obj.get("containedInPlace")),
    }
    return {k: v for k, v in trimmed.items() if v not in (None, [], {}, "")}


def json_size(obj: Any) -> int:
    """Size of ``obj`` as compact UTF-8 JSON — the budget :func:`trim_detail` is measured in."""
    return len(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
