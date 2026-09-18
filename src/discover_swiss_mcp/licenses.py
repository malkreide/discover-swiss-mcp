"""Licence gate, attribution and the test-object filter.

**Why a gate at all.** "Infocenter Open" is the name of the product, not a
statement about the licence of every object in it. The probe of 2026-09-17
found Guidle events carrying ``C-All-Rights-Reserved`` and HotellerieSuisse
hotel groups carrying no licence at all, sitting next to CC BY-SA museums in
the same index. A server that passes everything through republishes
all-rights-reserved content under an open banner.

So the rule is the other way round: an object is served **only** if its licence
normalises into :data:`ALLOWED`. Everything else is dropped and **counted** —
``excluded_by_license`` in the envelope — because an unexplained short list is
the shape that invites an invented answer.

**Where the licence comes from.** Detail objects (``/vertices/{id}``) and list
rows carry a root ``license``. Search hits do not: ``IndexResponse`` has 48
fields and ``license`` is not among them, so ``/search`` can never return one.
There the licence is derived from ``dataGovernance``: the origin whose
``datasource`` belongs to the object's own provider. Verified against both
detail fixtures — Landesmuseum (provider ``zht``, origin ``zht-cms`` → CC BY-SA,
matching its root licence) and Hotel Du Nord (provider ``hs``, origins ``hs``,
``hs-my``, ``hs-d365`` → CC BY, matching its root licence). The other origins of
those objects carry ``CC BY-NC-SA`` and ``C-All-Rights-Reserved`` for merged
sub-data, which is exactly why "first origin wins" would be the wrong rule.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel

# Normalised licence identifiers this server is willing to serve.
#
# The set is deliberately small and deliberately *not* derived from a "does it
# look open" heuristic. `CC BY-NC-*` is missing on purpose: non-commercial is a
# restriction an assistant's downstream use cannot honour on the user's behalf.
ALLOWED: frozenset[str] = frozenset({"CC0", "CC 0", "CC BY", "CC BY-SA", "CC BY-ND", "ODbL"})

# Normalisation collapses the spellings the index actually mixes: `CC-BY`,
# `cc by`, `CC  BY-SA`, `CC BY - SA`. Everything becomes upper case, hyphens
# between the scheme and the clauses become spaces, and runs of whitespace
# collapse to one.
_NORMALISE_ALLOWED = frozenset(
    " ".join(entry.upper().replace("-", " ").split()) for entry in ALLOWED
)

_TEST_NAME_PATTERN = re.compile(r"\b(demo|test|beispiel|muster|placeholder)\b", re.IGNORECASE)

# Placeholder values the probe found on «Demo Event» in the production index.
_PLACEHOLDER_STREETS = frozenset({"strasse 1", "musterstrasse 1"})
_PLACEHOLDER_POSTAL_CODES = frozenset({"plz"})
_PLACEHOLDER_LOCALITIES = frozenset({"ort"})
_PLACEHOLDER_EMAIL_DOMAINS = ("example.ch", "example.com")


class Attribution(BaseModel):
    """Per-object attribution, built from the object itself.

    ``copyright_notice`` is the source's own wording (e.g. «Zürich Tourismus
    www.zuerich.com») and is passed through verbatim, never reworded.
    """

    provider: str
    license: str
    copyright_notice: str | None
    source_url: str | None


def normalize_license(value: Any) -> str:
    """Normalise a licence string for comparison. Non-strings become ``""``."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.upper().replace("-", " ").split())


def license_of(obj: dict[str, Any]) -> str | None:
    """The licence that governs this object, or ``None`` if it has none.

    Root ``license`` first; falling back to the ``dataGovernance`` origin that
    belongs to the object's own provider (see the module docstring).
    """
    root = obj.get("license")
    if isinstance(root, str) and root.strip():
        return root.strip()

    governance = obj.get("dataGovernance")
    if not isinstance(governance, dict):
        return None
    origins = governance.get("origin")
    if not isinstance(origins, list):
        return None

    provider = governance.get("provider")
    acronym = None
    if isinstance(provider, dict):
        acronym = provider.get("acronym") or provider.get("identifier")

    def _origin_license(origin: Any) -> str | None:
        if isinstance(origin, dict):
            value = origin.get("license")
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    if isinstance(acronym, str) and acronym:
        prefix = acronym.lower()
        for origin in origins:
            if not isinstance(origin, dict):
                continue
            datasource = str(origin.get("datasource") or "").lower()
            if datasource == prefix or datasource.startswith(f"{prefix}-"):
                found = _origin_license(origin)
                if found:
                    return found

    # No provider, or no origin belonging to it: the object does not say which
    # licence governs *it*. Guessing from an unrelated origin is how
    # all-rights-reserved sub-data gets relabelled as open.
    return None


def is_allowed_license(value: Any) -> bool:
    """Whether a licence string normalises into :data:`ALLOWED`."""
    return normalize_license(value) in _NORMALISE_ALLOWED


def is_servable(obj: dict[str, Any]) -> bool:
    """Whether this object may be served at all."""
    return is_allowed_license(license_of(obj))


def is_no_derivatives(obj: dict[str, Any]) -> bool:
    """``True`` for an ND licence — the text may be quoted, not reworded.

    ``get_details`` uses this to tell the model that a description is to be
    passed on verbatim rather than paraphrased.
    """
    normalised = normalize_license(license_of(obj))
    return "ND" in normalised.split()


def _first_homepage_url(obj: dict[str, Any]) -> str | None:
    links = obj.get("link")
    if isinstance(links, list):
        for link in links:
            if isinstance(link, dict) and link.get("type") == "WebHomepage":
                url = link.get("url")
                if isinstance(url, str) and url:
                    return url
    url = obj.get("url")
    return url if isinstance(url, str) and url else None


def attribution(obj: dict[str, Any]) -> Attribution:
    """Build the attribution that travels with this object.

    Attribution belongs in the response, not in the README: the providers and
    licences differ per hit, and a note covering "the data" covers none of them.
    """
    governance = obj.get("dataGovernance")
    provider_name = "unknown"
    if isinstance(governance, dict):
        provider = governance.get("provider")
        if isinstance(provider, dict):
            candidate = provider.get("name") or provider.get("identifier")
            if isinstance(candidate, str) and candidate.strip():
                provider_name = candidate.strip()

    notice = obj.get("copyrightNotice")
    return Attribution(
        provider=provider_name,
        license=license_of(obj) or "unknown",
        copyright_notice=notice if isinstance(notice, str) and notice.strip() else None,
        source_url=_first_homepage_url(obj),
    )


def is_test_object(obj: dict[str, Any]) -> bool:
    """Whether this looks like a test record that slipped into production.

    «Demo Event» — «Strasse 1, PLZ Ort», ``mail@example.ch`` — sits next to real
    events in the live index. A tool that does not filter recommends a
    placeholder to a tourist; one that filters silently hides how thin the
    stock is. Hence: filtered **and** counted.
    """
    name = obj.get("name")
    if isinstance(name, str) and _TEST_NAME_PATTERN.search(name):
        return True

    address = obj.get("address")
    if isinstance(address, dict):
        street = str(address.get("streetAddress") or "").strip().lower()
        if street in _PLACEHOLDER_STREETS:
            return True
        if str(address.get("postalCode") or "").strip().lower() in _PLACEHOLDER_POSTAL_CODES:
            return True
        if str(address.get("addressLocality") or "").strip().lower() in _PLACEHOLDER_LOCALITIES:
            return True
        if _is_placeholder_email(address.get("email")):
            return True

    return _is_placeholder_email(obj.get("email"))


def _is_placeholder_email(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    candidate = value.strip().lower()
    return any(candidate.endswith(domain) for domain in _PLACEHOLDER_EMAIL_DOMAINS)


class Screened(BaseModel):
    """What survived the two gates, and how much did not."""

    kept: list[dict[str, Any]]
    excluded_by_license: int = 0
    excluded_test_objects: int = 0


def screen(objects: list[dict[str, Any]], *, drop_test_objects: bool = True) -> Screened:
    """Apply the licence gate and the test-object filter, counting both.

    The licence gate runs first: an all-rights-reserved test record is excluded
    by licence, and counting it twice would make the two numbers add up to more
    than the page that was fetched.
    """
    kept: list[dict[str, Any]] = []
    by_license = 0
    test_objects = 0
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        if not is_servable(obj):
            by_license += 1
            continue
        if drop_test_objects and is_test_object(obj):
            test_objects += 1
            continue
        kept.append(obj)
    return Screened(
        kept=kept,
        excluded_by_license=by_license,
        excluded_test_objects=test_objects,
    )
