#!/usr/bin/env python3
"""The default matrix: every parameter the spec offers on the endpoints this
server calls, and what the server does with it (audit FID-001).

The rows are derived from the recorded spec (``probes/probe_out/openapi.json``),
not written from memory: a parameter the spec gains shows up as a missing
decision and fails ``tests/test_defaults.py`` until someone decides. The
question each row answers is the one that makes a result silently incomplete:
*if this is not sent, does the upstream default narrow the answer?*

    python scripts/default_matrix.py           # print the matrix
    python scripts/default_matrix.py --write   # write docs/DEFAULTS.md
    python scripts/default_matrix.py --check   # exit 1 if docs/DEFAULTS.md is stale
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "probes" / "probe_out" / "openapi.json"
OUT = ROOT / "docs" / "DEFAULTS.md"

# The list endpoints the server calls: the five of the list fallback.
LIST_ENDPOINTS = (
    "places",
    "civicStructures",
    "foodEstablishments",
    "localbusinesses",
    "lodgingbusinesses",
)

FILTER = "not sent — a filter: absent means unrestricted"
TOOL = "sent when the caller asks for it (tool parameter); absent means unrestricted"
PERSONAL = "not sent — personalisation, needs an end-user token; off when absent"

ACCEPT_TIMEZONE = (
    "not sent — changes how dates are written (offset), not which objects match. "
    "find_events filters by calendar day in Europe/Zurich via OData. The upstream "
    "default zone is unmeasured; pinning it waits for a live comparison."
)
VALUE_SCOPE = (
    "not sent — selects provider values for a named client target; no target applies, "
    "the provider's standard values are the ones wanted"
)
RESPONSE_TRIM = "not sent — trims the response; default `all` keeps every entry"
CATEGORY_VERSION = "sent: `sui` (vendor advice Aug. 2025; no measured effect)"

SEARCH: dict[str, str] = {
    # headers
    "Ocp-Apim-Subscription-Key": "sent: the subscription key (SecretStr, never logged)",
    "Authorization": PERSONAL,
    "Accept-Language": "sent: the tool's `lang` (de, fr, it, en); default would be de-CH",
    "Accept-Timezone": ACCEPT_TIMEZONE,
    "scope": VALUE_SCOPE,
    # body — what the tools use
    "project": "sent always: `[dsod-content]`; without it /search answers 401",
    "searchText": "sent: the tool's `query`",
    "searchFields": (
        "sent `name` for `match='name'`; omitted for `match='all'`, whose default is all "
        "fields (probe 4) — audit FID-004"
    ),
    "select": "sent always: the fields a hit is built from (verified whitelist)",
    "currentPage": "sent always: the tool's `page`",
    "resultsPerPage": "sent always: the tool's `page_size`; default would be 10",
    "scoringReferencePoint": "sent with `near`: ranks by distance",
    "filters": "sent when needed: `geo.distance` radius and OData filters (length, ascent, difficulty, schedule)",
    "facets": "sent by explore_area and resolve_area: name, count, orderBy=count, orderDirection=desc",
    "facetOrder": "not sent — superseded by orderBy/orderDirection in each FacetRequest",
    "orderBy": "not sent — relevance, or distance with scoringReferencePoint, is the order wanted",
    "onlySuggestions": "not sent — when absent the full result is returned",
    "onlyWithAvailabilities": "not sent — acts only together with an availability filter, never set",
    "personalize": PERSONAL,
    "searchProfileName": PERSONAL,
    "scoringProfile": "not sent — spec: «if not set, the default scoring is applied»",
    "viewId": "not sent — a view would pre-set parameters the server does not see",
    "leafType": TOOL,
    "type": TOOL,
    "addressLocality": TOOL,
    "containedInPlace": TOOL + " (`region`, resolved to an area id)",
    "sourcePartner": TOOL + " (`accessible`: `pi`, `okgo`)",
    "starRatingValue": TOOL + " (`stars_min`)",
    "starRatingGarni": TOOL + " (`garni`)",
    "priceRange": TOOL + " (`price_range`, sent as 1/2/3)",
    "amenityFeature": TOOL + " (`amenities`)",
    "categoryTree": TOOL + " (`kind` for winter/cycling)",
    "season": TOOL + " (`season_month`)",
}
for _name in (
    "datasource",
    "award",
    "campaignTag",
    "profileTag",
    "allTag",
    "category",
    "scoringTag",
    "sourceId",
    "location",
    "hasGeoShape",
    "productAvailability",
    "action",
    "starRatingName",
    "starRatingSuperior",
    "numberOfRooms",
    "numberOfBeds",
    "openingHoursSpecificationDayOfWeek",
    "standardPrice",
    "suiCategoryTree",
    "tag",
    "addressPostalCode",
    "time",
    "length",
    "state",
    "ratingCondition",
    "ratingDifficulty",
    "elevationAscent",
    "elevationDescent",
    "elevationMinAltitude",
    "elevationMaxAltitude",
    "combinedType",
    "combinedTypeTree",
):
    SEARCH.setdefault(_name, FILTER)
for _name in ("scheduleStart", "scheduleEnd"):
    SEARCH[_name] = (
        "not sent — applied after the search, so `count` and paging miscount (discarded, "
        "see CHANGELOG); find_events sends the OData `schedule/any(...)` overlap in `filters`"
    )
# length, ratingDifficulty and elevationAscent are used — as OData in `filters`.
for _name in ("length", "ratingDifficulty", "elevationAscent"):
    SEARCH[_name] = "not sent as a body field — the tool sends it as OData in `filters` (probe 5.4)"

FACET: dict[str, str] = {
    "name": "sent: one of the eight verified OData names; anything else is not sent",
    "count": "sent: 20 (explore_area), 30 (resolve_area — stated in the hint when reached)",
    "orderBy": "sent: `count` (the documented default, relied upon)",
    "orderDirection": "sent: `desc` (the documented default, relied upon)",
    "scope": "not sent — default `current`: values counted over the current result, as reported",
    "project": "not sent — the request itself is already scoped to dsod-content",
    "excludeRedundant": "not sent — default false: no value is dropped",
    "key": "not sent — one facet per name; the answer is read by name",
    "responseName": "not sent — the default name is the one the reader looks up",
    "interval": "not sent — value facets only, no ranges",
    "values": "not sent — value facets only, no ranges",
    "selectValues": "not sent — every value, not a chosen subset",
    "filterValues": "not sent — every value, not a chosen subset",
    "additionalType": FILTER,
}

VERTEX: dict[str, str] = {
    "id": "sent: the identifier, after the shape gate (nothing is sent for an invalid one)",
    "Ocp-Apim-Subscription-Key": SEARCH["Ocp-Apim-Subscription-Key"],
    "Accept-Language": SEARCH["Accept-Language"],
    "Accept-Timezone": ACCEPT_TIMEZONE,
    "scope": VALUE_SCOPE,
    "ds-tagFilter": RESPONSE_TRIM,
    "ds-containedInPlaceFilter": RESPONSE_TRIM + " (probe finding 6: it is not a hit filter)",
    "ds-categoryFilter": RESPONSE_TRIM,
    "categoryVersion": CATEGORY_VERSION,
    "project": "sent always: `dsod-content`",
    "containedInPlace": FILTER,
    "select": "not sent — the full object is read and trimmed server-side to about 8 KB",
    "photoSeason": FILTER,
    "includeAllPhotos": "sent: `false` (documented default: low-confidence images skipped)",
}

LIST: dict[str, str] = {
    "Ocp-Apim-Subscription-Key": SEARCH["Ocp-Apim-Subscription-Key"],
    "Accept-Language": SEARCH["Accept-Language"],
    "Accept-Timezone": ACCEPT_TIMEZONE,
    "scope": VALUE_SCOPE,
    "ds-tagFilter": RESPONSE_TRIM,
    "ds-containedInPlaceFilter": VERTEX["ds-containedInPlaceFilter"],
    "ds-categoryFilter": RESPONSE_TRIM,
    "categoryVersion": CATEGORY_VERSION,
    "project": "sent always: `dsod-content`; without it an undocumented partner default applies",
    "top": "sent always: 1000 in the fallback (FALLBACK_TOP; the token is followed, as `top` is a wish), 200 otherwise; default would be 10",
    "select": "sent always: the list whitelist (about 1 KB per object instead of 9.5 KB)",
    "includeCount": "sent: `true` on the first page, `false` on the following ones",
    "continuationToken": "sent when paging: the `nextPageToken` of the previous page",
    "containedInPlace": "sent when the fallback has an area id; absent means unrestricted",
    "descriptionMode": "not sent — default `full`: the description stays whole",
    "photoSeason": FILTER,
    "includeAllPhotos": "not sent — the list select carries no photo array",
}
for _name in (
    "category",
    "updatedSince",
    "datasource",
    "identifiers",
    "parentOrganization",
    "additionalType",
):
    LIST.setdefault(_name, FILTER)

# Sent although the spec does not list them for that endpoint.
EXTRA = {
    "User-Agent": "`discover-swiss-mcp/<version>` with the repository URL, on every request",
    "Accept": "`application/json`, on every request",
    "categoryVersion on /search": "`sui` — sent with every request, listed in the spec for list and detail only",
}


def spec_parameters() -> dict[str, list[str]]:
    """Parameter names per group, read from the recorded spec."""
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    paths = spec["paths"]
    definitions = spec["definitions"]

    search = [p["name"] for p in paths["/search"]["post"]["parameters"] if p["in"] != "body"]
    search += list(definitions["SearchRequest"]["properties"])
    facet = list(definitions["FacetRequest"]["properties"])
    vertex = [p["name"] for p in paths["/vertices/{id}"]["get"]["parameters"]]
    listed: list[str] = []
    for endpoint in LIST_ENDPOINTS:
        for parameter in paths[f"/{endpoint}"]["get"]["parameters"]:
            if parameter["name"] not in listed:
                listed.append(parameter["name"])
    return {"search": search, "facet": facet, "vertex": vertex, "list": listed}


DECISIONS = {"search": SEARCH, "facet": FACET, "vertex": VERTEX, "list": LIST}
TITLES = {
    "search": "`POST /search` — headers and SearchRequest body",
    "facet": "FacetRequest — each entry of `facets` in a search",
    "vertex": "`GET /vertices/{id}` — get_details",
    "list": "`GET` list endpoints — the list fallback (" + ", ".join(LIST_ENDPOINTS) + ")",
}


def undecided() -> dict[str, list[str]]:
    """Spec parameters without a decision, per group. Empty when complete."""
    params = spec_parameters()
    return {
        g: [p for p in names if p not in DECISIONS[g]]
        for g, names in params.items()
        if any(p not in DECISIONS[g] for p in names)
    }


def stale_decisions() -> dict[str, list[str]]:
    """Decisions for parameters the spec no longer lists."""
    params = spec_parameters()
    return {
        g: sorted(set(d) - set(params[g])) for g, d in DECISIONS.items() if set(d) - set(params[g])
    }


def render() -> str:
    params = spec_parameters()
    lines = [
        "# Default matrix",
        "",
        "Every parameter the recorded spec (`probes/probe_out/openapi.json`, release",
        "20260910.2) offers on the endpoints this server calls, and what the server",
        "does with it. Generated by `scripts/default_matrix.py`; do not edit by hand —",
        "`tests/test_defaults.py` fails when this file and the script disagree, and when",
        "the spec lists a parameter without a decision.",
        "",
        "The question behind every row: *if this is not sent, does the upstream default",
        "narrow the answer?* Where it would, the parameter is sent (audit FID-001).",
        "",
    ]
    for group in ("search", "facet", "vertex", "list"):
        lines += [f"## {TITLES[group]}", "", "| Parameter | Server |", "|---|---|"]
        lines += [f"| `{name}` | {DECISIONS[group][name]} |" for name in params[group]]
        lines.append("")
    lines += ["## Sent outside the spec's parameter lists", "", "| Header | Server |", "|---|---|"]
    lines += [f"| {name} | {decision} |" for name, decision in EXTRA.items()]
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    missing = undecided()
    if missing:
        print(f"Spec parameters without a decision: {missing}", file=sys.stderr)
        return 1
    text = render()
    if "--write" in argv:
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
        return 0
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)} is stale; run with --write", file=sys.stderr)
            return 1
        print(f"{OUT.relative_to(ROOT)} is current")
        return 0
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
