# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Not released. Release gate: written confirmation of the search entitlement by
discover.swiss (README «Status»).

### Added

- **Eight read-only tools**, each a pure `*_impl` function in `tools.py` plus
  an MCP wrapper in `server.py` (`readOnlyHint: true`, `openWorldHint: true`):
  - `search` — full text over the whole index (`match: all|name`, the latter
    sent as `searchFields=name`), `types`, `locality`, `near` with optional
    `radius_km` (`geo.distance`, a real radius filter). Rooms and meeting rooms
    are excluded unless `types` asks for them and counted in
    `excluded_by_default_types`.
  - `get_details` — `/vertices/{id}`, trimmed to ~8 KB (3 photos, amenity
    names, provider and licence instead of the governance chain), HTML and
    entities resolved to text, `no_derivatives` for CC BY-ND, disclaimer B.
  - `find_accommodation` — stars, garni, price band (`Niedrig`/`Mittel`/`Hoch`
    sent as 1/2/3), amenities, `accessible` (partners `pi`, `okgo`), distance.
  - `find_tours` — `kind` by measured `leafType`/`categoryTree` mapping
    (`probes/PROBE_TOURKINDS_discover-swiss.md`), difficulty, length, ascent,
    season month, region, distance.
  - `find_events` — date range (default today + 30 days, Europe/Zurich) as the
    OData overlap filter on `schedule`. The `nextOccurrence` sentinel
    2099-12-31 becomes `date_open: true` with «Termin offen».
  - `webcams_near` — `geo.distance` radius (default 25 km) or region;
    `live_url` from `link[]`, `snapshot_url` labelled as a stored still.
  - `explore_area` — facet counts for a region, locality or radius; only the
    eight verified OData facet names are sent, anything else is reported in
    `missing_facets`.
  - `source_status` — reachability, search availability, calls per minute,
    quota state, last success, cache entries, index size, coverage and the
    entitlement state from `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED`. Works
    without a key.
- **Response envelope** (`models.py`) on every tool: `source`, `provenance`
  (`live_api`/`cached`/`list_fallback`), `retrieved_at`, `source_freshness`,
  `project`, `degraded`, `disclaimer`, `hint`, and the three counters
  `excluded_by_license`, `excluded_test_objects`, `excluded_by_default_types`.
  Paged tools add `upstream_count`, `fetched`, `returned` and `applied` (the
  scope actually sent).
- **Licence whitelist** on the object's licence — root `license` on detail
  objects, first `dataGovernance.origin` on search hits
  (`probes/PROBE_LICENSE_discover-swiss.md`): CC0, CC BY, CC BY-SA, CC BY-ND,
  ODbL are served; everything else is withheld and counted. Per-hit
  `attribution` (provider, licence, copyright notice).
- **Test-object filter**: «Demo Event», placeholder addresses («Strasse 1»,
  «PLZ», «Ort») and `example.ch` mail addresses are withheld and counted.
- **List fallback** in `search` and `find_accommodation`: on a refused
  `/search` (401/403) they read the typed list endpoints, filter by locality
  and distance client-side, and answer `provenance: list_fallback`,
  `degraded: search_unavailable`, with a hint naming what was ignored. At most
  eight list calls per tool call; an incomplete scan is stated.
- **Client**: client-side rate bucket of 55 calls/min under the published 60, retries 2 s/4 s/8 s on 5xx and network
  errors, 429 waits the seconds the upstream names, `403` with «quota» is the
  state `quota_exhausted` and never retried; cache 15 min (search), 60 min
  (facets), 24 h (detail); SSRF guard with DNS pinning; pinned protocol
  version; structlog JSON to stderr; the key as `SecretStr`, never logged.
- **Tool hash snapshot** (`docs/tool-hashes.json`, `scripts/gen_tool_hashes.py`),
  checked by the test suite — the `openlex-mcp` pattern.
- **Live canaries** (`tests/test_live.py`, marker `live`, key from the
  environment, excluded from CI): recall floors at half of the 2026-09-17
  counts for all eight tool paths, fidelity canaries (`match="name"` narrows,
  `containedInPlace/id` comes back, Landesmuseum description without
  entities), the distance canary (nearest hotel to Interlaken is in
  Interlaken) and the filter canary (demo event counted; skips, not fails, if
  it is gone upstream).
- **Documentation**: bilingual README with scope map, anchor demo queries,
  architecture decision, known limitations, attribution duty and entitlement
  status; `docs/DEMO.md` with the tool chain for each anchor query;
  `docs/LICENSES.md`.
- **Audit** `audits/AUDIT_2026-09-26.md` (mcp-audit, full run, 85 applicable
  checks plus four server-specific fidelity checks) and its run directory.
- Scripts: `scripts/p2_anchor_run.py` (anchor queries live),
  `scripts/p3_stopgate_run.py` (`explore_area` and `source_status` live),
  `scripts/validate_repo.py`, `scripts/check_release_artifacts.py`.
- Scaffold: src layout, `pyproject.toml`, `server.json`, CI and publish
  workflows (actions pinned by SHA), Dependabot.

### Changed

- `DiscoverSwissClient.search` reads its cache before refusing a call while
  search is unavailable — a cached area lookup keeps working in fallback mode.
- `search` says in its description that with a `query`, text relevance
  outweighs distance in the ranking (live: Hiltl at 0.58 km ranked fifth
  behind 3.5 km).
- `find_tours` says that every filter only matches tours carrying the value;
  `season_month` keeps 20 of 178 walking tours for July. The empty hint says
  to drop it first.

### Fixed

- **Every live search hit was withheld as unlicensed.** Search hits carry no
  root `license` and no `dataGovernance.provider`, only `origin`. The licence
  of a hit is now the one of its first origin — measured against the detail
  objects' root licence: 15 of 15 live hits, 105 of 105 recorded objects. The
  same change fixes contentdesk tours and webcams, whose provider `tso-ctd`
  never matched its datasources `ctd-*` by prefix.
- **`find_tours(kind=...)` sent three tour types the index does not have**
  (`CyclingRoute`, `MountainBikeRoute`, `SnowshoeTrail`): `cycling` and `mtb`
  always answered empty, `winter` missed all 23 snowshoe tours. The mapping is
  now measured.
- **`explore_area` failed on an unknown facet name.** The live stop-gate run
  (2026-09-26) answered an invented name with HTTP 400 for the whole request.
  Only the eight verified names are sent now; anything else is reported in
  `missing_facets` with a hint.
- **The server did not start on Windows.** `zoneinfo` needs the `tzdata`
  package there; it is now a dependency on Windows.
- The hint for a page whose hits were all withheld names each reason with its
  count and suggests `types` only when rooms were among them.

### Known findings from the live probe (2026-09-17)

The twelve findings of `probes/PROBE_REPORT_discover-swiss-mcp.md`, section 10,
numbered as there. Each one contradicts the vendor documentation or would have
made a tool silently wrong; the recorded response is what settles it.

1. **The documentation denies search; the API grants it.** The docs state
   "You can't use the search functionality" for this subscription. Live: HTTP
   200 with a project. Written confirmation is a release gate.
2. **`demo-web` is partner-bound.** The example project from the docs answers
   400. Projects come from `/projects`.
3. **Paging is `nextPageToken`, not `continuation`.** `hasNextPage` is a
   boolean, not a token; sending it answers 400.
4. **`top=1000` does not mean 1000.** Cosmos DB cuts at roughly 4 MB (460
   rooms) — follow the token instead of trusting the count.
5. **An open product is not an open licence.** Guidle events arrive as
   All-Rights-Reserved, hotel groups with no licence at all. Hence the
   whitelist.
6. **`ds-containedInPlaceFilter` is not a filter.** The header decides which
   `containedInPlace` entries appear in the response; the hit filter is the
   query parameter.
7. **Schweiz Tourismus already supplies data** — `sourcePartner` on 2,769
   hotels, datasource `st-sc`. Their data already flows through the open
   channel.
8. **Facet names are ignored silently.** `containedInPlace` and
   `ratingDifficulty` produce no facet and no error — the OData spellings do.
   Response keys are checked against the request.
9. **One hotel weighs 78 KB.** 40 photos, 81 amenities, governance chains per
   origin. The detail tool is a filter, not a pass-through.
10. **There is test data in the production index.** A «Demo Event» at
    «Strasse 1, PLZ Ort» sits next to real events.
11. **Descriptions are HTML with entities.** `&uuml;` instead of ü, prices as
    tables. Resolved server-side, or the model invents the encoding away.
12. **Half the index is rooms and meeting rooms** (9,838 of 20,817). Without a
    type default, a tourist finds 61 double rooms first.

### Further findings after the probe report

Found while building (P2–P4); recorded here so they are not lost between the
report and the code.

- **`geo.distance` is a real radius filter**, not only a ranking — in the
  filter documentation, not in the spec.
- **The convenient event filter miscounts.** `scheduleStart`/`scheduleEnd`
  apply after the search, so `count` and paging stop being reliable. The OData
  path is clumsier and correct.
- **`nextOccurrence` has a sentinel: 2099-12-31.** Passed through unchecked,
  an assistant recommends an event on 31 December 2099.
- **Two areas are called «Zürich»** (`osm_1690227`, 894 objects;
  `kire_zurich`, 785), and the larger does not come first. `resolve_area` takes
  the larger, sets `ambiguous` and names the other in the hint.
- **An unknown facet name is not always dropped quietly.** The probe saw the
  `filterPropertyName` spellings vanish; an invented name answered 400 for the
  whole request.

### Discarded

Decisions taken against an option, with the reason, so the option is not
reopened without new evidence.

- **Project `dsod-hs`** — a subset of `dsod-content` (4,476 hotels); one
  project only.
- **`scheduleStart`/`scheduleEnd` for events** — miscounts (see above); the
  OData `schedule/any(...)` filter is used instead.
- **`ds-containedInPlaceFilter` header as area filter** — it trims the
  response; the `containedInPlace` query parameter filters.
- **Paging `/areas` to resolve a region name** — 7,290 rows per lookup; the
  `containedInPlace/id` facet answers in one call.
- **Tools for booking, availability, weather, journeys and image thumbnails**
  — Marketplace product, not in the Infocenter; `meteoswiss-mcp` and
  `swiss-transport-mcp` cover weather and journeys; the media service is
  closed to this subscription.
- **A standalone `fastmcp` dependency** — the official `mcp` SDK 2.x is the
  portfolio stack.
