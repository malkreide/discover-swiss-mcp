# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
