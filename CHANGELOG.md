# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **The server did not start on Windows.** `find_events` resolves «today» in
  `Europe/Zurich` through `zoneinfo`, which on Windows needs the `tzdata`
  package; without it, importing the tools raised `ZoneInfoNotFoundError`.
  `tzdata` is now a dependency on Windows.
- **`explore_area` failed on an unknown facet name.** The probe had seen the
  API drop the `filterPropertyName` spellings quietly and the tool assumed the
  same for any name; the live stop-gate run (2026-09-26) answered an invented
  name with HTTP 400 for the whole request. Only the eight verified names are
  sent now; anything else is reported in `missing_facets` with a hint.

### Added

- P3: the remaining four tools, each a pure `*_impl` function plus an MCP
  wrapper (`readOnlyHint`, `openWorldHint`):
  - `find_events` — date range (default today + 30 days, Europe/Zurich) as the
    OData overlap filter on `schedule` (PROBE_VERIFY 4), never
    `scheduleStart`/`scheduleEnd`. The `nextOccurrence` sentinel 2099-12-31
    becomes `next_occurrence: null`, `date_open: true`, `date_note` «Termin
    offen»; a missing `nextOccurrence` falls back to the schedule. «Demo
    Event» and all-rights-reserved Guidle events are withheld and counted.
  - `webcams_near` — `geo.distance` radius (default 25 km) or region;
    `live_url` from `link[]` (`WebDetail`/`WebLink`), `snapshot_url` labelled
    as a stored still.
  - `explore_area` — facet counts for a region, locality or radius. Short
    facet names (`containedInPlace`, `ratingDifficulty`, `addressLocality`)
    are mapped to their OData names before sending; a name the API drops
    silently is reported in `missing_facets` with a hint.
  - `source_status` — reachability, search availability, calls per minute,
    quota state, last success, cache entries, index size (from an unfiltered
    `explore_area`, cached 60 min), coverage and the entitlement state from
    `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED`. Works without a key.
- List fallback wired into `search` and `find_accommodation`: on a refused
  `/search` they read `/places`, `/civicStructures`, `/foodEstablishments`,
  `/localbusinesses`, `/lodgingbusinesses` (by `types`), filter by locality and
  distance client-side, and answer `provenance: list_fallback`,
  `degraded: search_unavailable`, with a hint naming what was ignored. At most
  eight list calls per tool call; an incomplete scan is stated.
- `scripts/p3_stopgate_run.py`: `explore_area` for «Glarnerland» and
  `source_status` against the live API, key from the environment only.

### Changed

- `DiscoverSwissClient.search` reads its cache before refusing a call while
  search is unavailable — a cached area lookup keeps working in fallback mode.
- Tool hash snapshot (`docs/tool-hashes.json`) now covers eight tools.

### Fixed

- **`find_tours(kind=...)` sent three tour types the index does not have**
  (`CyclingRoute`, `MountainBikeRoute`, `SnowshoeTrail`): `cycling` and `mtb`
  always answered empty, `winter` missed all 23 snowshoe tours. The mapping
  is now measured (`probes/PROBE_TOURKINDS_discover-swiss.md`): walking by
  seven `leafType` values, winter and cycling by the full `categoryTree`
  path — the short code answers 0 without an error.
- `find_tours` now says that every filter only matches tours carrying the
  value; `season_month` keeps 20 of 178 walking tours for July. The empty
  hint says to drop it first.
- `search` now says that with a `query`, text relevance outweighs distance
  in the ranking (live: Hiltl at 0.58 km ranked fifth behind 3.5 km).

- **Every live search hit was withheld as unlicensed.** Search hits carry no
  root `license` and no `dataGovernance.provider`, only `origin`; the P1 rule
  needed the provider and found nothing. The licence of a hit is now the one
  of its first origin — measured against the detail objects' root licence:
  15 of 15 live hits, 105 of 105 recorded objects
  (`probes/PROBE_LICENSE_discover-swiss.md`). The same change fixes
  contentdesk tours and webcams, whose provider `tso-ctd` never matched its
  datasources `ctd-*` by prefix.
- The hint for a page whose hits were all withheld now names each reason with
  its count and suggests `types` only when rooms were among them.

### Added

- P2: the four core tools `search`, `get_details`, `find_accommodation` and
  `find_tours`, each a pure `*_impl` function in `tools.py` plus an MCP
  wrapper in `server.py` (`readOnlyHint`, `openWorldHint`). Every hit passes
  the licence gate and the test-object filter first; `upstream_count`,
  `fetched`, `returned` and the three `excluded_*` counters make every
  shortfall visible. Empty results carry a concrete `hint`.
- Envelope field `excluded_by_default_types`: rooms and meeting rooms that
  `search` leaves out unless `types` asks for them.
- Tool hash snapshot (`docs/tool-hashes.json`, `scripts/gen_tool_hashes.py`),
  checked by the test suite — the `openlex-mcp` pattern.
- `scripts/p2_anchor_run.py`: the three anchor queries of the probe report
  against the live API, key from the environment only.

- Scaffold: src layout, packaging metadata (`pyproject.toml`, `server.json`),
  CI and publish workflows, Dependabot, bilingual README, licence and data
  licence documentation. No tools are registered yet.
- Response envelope (`models.py`) with `source`, `provenance`, `retrieved_at`,
  `source_freshness`, `project`, `degraded`, `disclaimer`, `hint`,
  `excluded_by_license`, `excluded_test_objects`, plus per-object
  `Attribution`.
- Configuration from environment variables; the subscription key is held as a
  `SecretStr` and never logged.

### Known findings from the live probe (2026-09-17)

Recorded here because each one contradicts the vendor documentation, and the
recorded response is what settles it. Full detail in
`probes/PROBE_REPORT_discover-swiss-mcp.md`.

1. **The documentation denies search; the API grants it.** The docs state
   "You can't use the search functionality" for this subscription. Live: HTTP
   200 with a project. Written confirmation is a release gate.
2. **`demo-web` is partner-bound.** The example project from the docs answers
   400. Projects come from `/projects`.
3. **Paging is `nextPageToken`, not `continuation`.** `hasNextPage` is a
   boolean, not a token; sending it answers 400.
4. **`top=1000` does not mean 1000.** Cosmos DB cuts at roughly 4 MB — follow
   the token instead of trusting the count.
5. **An open product is not an open licence.** Guidle events arrive as
   All-Rights-Reserved, hotel groups with no licence at all. Hence the
   whitelist on the root `license` field.
6. **`ds-containedInPlaceFilter` is not a filter.** The header decides which
   `containedInPlace` entries appear in the response; the hit filter is the
   query parameter.
7. **Facet names are ignored silently.** `containedInPlace` and
   `ratingDifficulty` produce no facet and no error — the OData spellings do.
   Response keys must be checked against the request.
8. **One hotel weighs 78 KB.** 40 photos, 81 amenities, governance chains per
   origin. The detail tool is a filter, not a pass-through.
9. **There is test data in the production index.** A "Demo Event" at
   "Strasse 1, PLZ Ort" sits next to real events.
10. **Descriptions are HTML with entities.** `&uuml;` instead of ü, prices as
    tables. Resolved server-side, or the model invents the encoding away.
11. **Half the index is rooms and meeting rooms** (9,838 of 20,817). Without a
    type default, a tourist finds 61 double rooms first.
12. **The convenient event filter miscounts.** `scheduleStart`/`scheduleEnd`
    apply after the search, so `count` and paging stop being reliable — the
    documentation says so itself. The OData path is clumsier and correct.
13. **`nextOccurrence` has a sentinel: 2099-12-31.** Passed through unchecked,
    an assistant recommends an event on 31 December 2099.
