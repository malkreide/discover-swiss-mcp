# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Not released. Release gate: written confirmation of the search entitlement by
discover.swiss (README «Status»).

### Release status

- **2026-09-26 — release on hold.** The release step (PyPI and MCP registry
  0.1.0, public reference instance on Railway, portfolio status, gate G1 over
  the remote endpoint) stopped at its precondition: discover.swiss's written
  confirmation of search on Infocenter Open, and of operating a public,
  non-commercial reference instance, is not on record.
  `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED` stays `pending`. Nothing was tagged or
  published. Instead `docs/DEMO.md` gained *Run locally with your own key*.

### Security

P5 — remediation of the audit of 2026-09-26. Each entry names its finding.

- **Inbound OAuth for the HTTP transport** (SEC-003, SEC-002): the server acts
  as an OAuth resource server. Scope hierarchy `mcp:tools-basic` (discovery,
  `source_status`) and `tourism:read:public` (every data tool); no write or
  admin scope, because no tool writes. Tokens are checked by introspection
  (RFC 7662): active, unexpired, `iss` = configured issuer, `aud` contains the
  resource URL (RFC 8707). Scopes are checked per call from the JSON-RPC body;
  401/403 carry `WWW-Authenticate` with the missing scope and the metadata URL;
  `/.well-known/oauth-protected-resource` (RFC 9728) names every scope. Off on
  stdio. New module `auth.py`.
- **HTTP bind policy** (SEC-016): any bind address other than loopback is
  refused at start-up (exit 2) unless inbound OAuth and
  `DISCOVER_SWISS_MCP_ALLOWED_HOSTS` are configured; an allowed network bind is
  logged as the warning `http_bind_non_loopback`. New module `http_app.py`.
- **Port-exact Host and Origin checks, always on** (SEC-024): the lists are
  passed to the SDK explicitly; on loopback `127.0.0.1:<port>` instead of the
  SDK's `127.0.0.1:*`, which let another local port through. Allowed hosts
  refuse wildcards; a name without a port is exact (the Host behind an HTTPS
  ingress).
- **SSRF: IPv4 embedded in IPv6** (SEC-004): IPv4-mapped (`::ffff:169.254.169.254`),
  6to4 and Teredo addresses are unwrapped before the blocklist; multicast,
  reserved and unspecified addresses are blocked too.
- **Hardened container and Kubernetes manifests** (SEC-007): `Dockerfile` with
  UID/GID 10001, no login shell, no bytecode writes, base image pinned by
  digest; `deploy/k8s/deployment.yaml` with `runAsNonRoot`,
  `readOnlyRootFilesystem`, `capabilities.drop: [ALL]`,
  `allowPrivilegeEscalation: false`, seccomp `RuntimeDefault`, memory `/tmp`.
  Measured on a built image: `docs/network-egress.md`.
- **Network-layer egress control** (SEC-021): `deploy/k8s/networkpolicy.yaml`
  (DNS plus TCP 443 to public ranges only), `deploy/k8s/cilium-networkpolicy.yaml`
  (host names), `docs/network-egress.md` with the allowed hosts per layer, the
  DNS path and the update procedure; a test holds policy, code allow-list and
  documentation together.
- **Secret scan in CI** (ARCH-005): a `secret-scan` job runs gitleaks v8.30.1
  (image pinned by digest) over the full history, with `.gitleaks.toml` adding
  the discover.swiss key format the default rules missed. `.env.example` with
  placeholders.

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
- **Live canaries for status and the fallback** (DRIFT-004, OPS-001): `/status`,
  `source_status` and each of the five list endpoints the fallback reads, with
  the current `select`; the module shares one client and one event loop.
- **Live canaries** (`tests/test_live.py`, marker `live`, key from the
  environment, excluded from CI): recall floors at half of the 2026-09-17
  counts for six tools (`search`, `find_accommodation`, `find_tours`,
  `find_events`, `webcams_near`, `explore_area`) plus the Zürich Tourismus
  partner scope through the client; a fidelity canary for `get_details`
  (Landesmuseum description contains «Hauptbahnhof», no HTML entity); no
  canary yet for `source_status` (audit OPS-001). Further fidelity canaries:
  `match="name"` narrows, `containedInPlace/id` comes back. The distance
  canary (nearest hotel to Interlaken is in Interlaken) and the filter canary
  (demo event counted; skips, not fails, if it is gone upstream).
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

- **Every wait counts against the 25 s call budget** (ARCH-014): a 429's named
  wait and the client-side token bucket no longer extend it (one call could
  reach about 55 s, past the MCP client's 30 s). A wait that does not fit ends
  the call at once with the new state `degraded: rate_limited` and the seconds
  in `hint`; `source_status` reports a rate limit as such, not as unreachable.
- **Own time seams** (OPS-010): `client._monotonic` next to `client._sleep`; no
  test patches `time.monotonic` any more. A real-time budget test and guards
  on both seams; the counter-test procedure is in CONTRIBUTING.md.
- **Facet requests send their ordering** (FID-001): `orderBy=count`,
  `orderDirection=desc`; `get_details` sends `includeAllPhotos=false`.
  `docs/DEFAULTS.md` lists all 118 parameters the spec offers on the endpoints
  used, with the server's decision for each — generated from the spec by
  `scripts/default_matrix.py`, held complete by `tests/test_defaults.py`.
- **Tool descriptions** (FID-005): `search` names its query syntax as plain
  words and says that operators, wildcards and prefixes are undocumented and
  untested, instead of an unmeasured «whole words, compounds not by their
  parts»; `find_events` and `webcams_near` no longer explain an empty result
  (their `hint` does). These reword sentences the P2/P3 briefs fixed verbatim.
  `probes/probe_query_syntax.py` measures the syntax.
- **`serverInfo.version`** is the package version (ARCH-016; was `""`). The
  version lives in the leaf module `_version.py` (ARCH-022). A test holds the
  protocol pin equal to the SDK's `LATEST_PROTOCOL_VERSION` and the comment
  above it says what it does not do (ARCH-012).
- **Dependencies capped** (DEP-001): `httpx<1`, `pydantic<3`; `uvicorn` and
  `starlette` are declared, being imported directly; Dependabot covers pip and
  docker.
- **README**: phases and gates (OPS-003), the new variables, container use.

- `DiscoverSwissClient.search` reads its cache before refusing a call while
  search is unavailable — a cached area lookup keeps working in fallback mode.
- `search` says in its description that with a `query`, text relevance
  outweighs distance in the ranking (live: Hiltl at 0.58 km ranked fifth
  behind 3.5 km).
- `find_tours` says that every filter only matches tours carrying the value;
  `season_month` keeps 20 of 178 walking tours for July. The empty hint says
  to drop it first.

### Fixed

- **A moved root key no longer reads as «no hit»** (FID-006): a `/search` or
  list answer whose rows cannot be read while its count says there are some
  raises the new state `degraded: upstream_shape_changed`; a genuine zero stays
  an empty result.
- **`get_details` called an upstream 4xx «unknown identifier»** (FID-003): only
  an identifier refused by the shape gate or a 404 says that now.
- **The list fallback's ignored filters are a field** (DRIFT-002):
  `ignored_parameters` lists what the answer did not apply (`query`;
  `stars_min`, `garni`, `price_range`, `amenities`, `accessible`).
- **`resolve_area` said «no area is named X» about data it never saw**
  (FID-L02): a missing `containedInPlace/id` facet is `upstream_shape_changed`;
  a comparison over the truncated 30 values says so.
- **`get_details` served test objects** (FID-L03): withheld and counted like in
  every list tool.
- **A DNS failure read as «blocked by egress policy»** (SEC-028): resolution
  failures are `ResolutionError`, retried like connection errors; `EgressError`
  is reserved for policy.

Follow-ups from the targeted re-verification (see «Re-verification after P5»):

- **An authorization-server outage locked valid tokens out for a minute**
  (SEC-002, SEC-028 regression): an unreachable, non-200 or non-JSON
  introspection answer is now `IntrospectionUnavailableError`, answered with
  503 `temporarily_unavailable` and `Retry-After: 10`, never as
  `invalid_token` and never cached.
- **Introspection answers without `iss` were accepted** (SEC-002 criterion 5):
  `iss` is required and must equal the configured issuer.
- **The caller's identity is logged per call** (SEC-002 criterion 4):
  `authorized_call` with `client_id`, `subject`, method and tool — never the
  token.
- **The OAuth client secret appeared in `repr(AuthConfig)`** (ARCH-005
  regression): the field is excluded from the repr.
- **The metadata document ignored the Host check** (SEC-024): a foreign `Host`
  gets 421 before anything is answered, the metadata included.
  `DISCOVER_SWISS_MCP_ALLOWED_ORIGINS` refuses wildcards like the host list.
- **A bucket wait did not count against the budget** (ARCH-014, OPS-010): the
  request after a rate-limiter wait got a fresh 25 s instead of what was left;
  the remainder is now measured after the wait. The `Retry-After` header path
  has its test.
- **Rows nested one level deeper read as «withheld: not openly licensed»**
  (FID-006): rows present but none with an `identifier` are
  `upstream_shape_changed`.
- **The query syntax of `search` is measured and stated** (FID-005):
  `probes/probe_query_syntax.py`, report `probes/PROBE_QUERY_discover-swiss.md`.
  Whole words, case-insensitive, all words required; no prefixes, `*`, `?`,
  `~`, `AND`/`OR` or `-` exclusion; quotes change nothing. The description and
  the `query` field say so; an empty result after such syntax starts its
  `hint` with it. Changes the tool hash of `search`.
- **The demo-event canary looked in a 30-day window** and skipped without
  telling whether the record or the filter was gone. It now looks the record
  up by name and skips only when the source itself reports none. A new canary
  holds the measured query syntax.

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

### Audit findings (2026-09-26)

Full mcp-audit run against `bd0e371`: 85 applicable checks, 25 pass, 38 partial, 18 fail, 4 not verified; four server-specific FID checks (FID-L01 pass, FID-L02 partial, FID-L03 partial, FID-L04 pass). Report: `audits/AUDIT_2026-09-26.md`. Not production-ready. Every open finding is listed with its disposition — *fix before release* (a release blocker besides the entitlement gate), *planned*, *accepted* (with the reason) or *fixed*.

| Check | Severity | Result | Disposition | Reason / action |
|---|---|---|---|---|
| ARCH-005 | critical | partial | fix before release | Add .env.example with placeholders and a '!.env.example' exception in .gitignore; add a secret scan step to CI. |
| FID-001 | critical | partial | fix before release | Derive the default matrix from the spec for the members still unpinned (FacetRequest count/scope, includeAllPhotos on /vertices, Accept-Timezone) and state the facet value limit (count=30) used by resolve_area in the result. |
| SEC-002 | critical | partial | accepted | The HTTP transport has no inbound authentication; client tokens are never forwarded upstream (verified). The server is local-only by design (loopback default). Catalogue question recorded in the audit: auth_model 'API-Key' here means a bring-your-own upstream key, not inbound auth. Accepted together with the SEC-016 fix that refuses a non-loopback bind without explicit opt-in. |
| SEC-004 | critical | partial | fix before release | IPv4-mapped IPv6 addresses bypass the blocklist (::ffff:169.254.169.254, ::ffff:127.0.0.1 verified). Unwrap ipv4_mapped before the check; add tests. |
| SEC-016 | critical | partial | fix before release | A 0.0.0.0 bind is silent. Refuse a non-loopback bind unless DISCOVER_SWISS_MCP_ALLOW_REMOTE=1 is set, and log a warning when it is. |
| ARCH-013 | high | partial | planned | Add a test for the main() to streamable_http_app(host=...) seam. |
| ARCH-014 | high | partial | fix before release | The 25 s budget can reach about 55 s after a 429 and rate-limiter waits are outside it; count both into the budget. Jitter stays off by design (single process behind a token bucket) and the reason is written next to RETRY_DELAYS. |
| ARCH-015 | high | partial | accepted | The SDK (mcp 2.2.0) still answers a legacy initialize over HTTP and issues mcp-session-id; the server keeps no state of its own. Accepted until the SDK offers a switch; re-check at the next SDK minor. |
| ARCH-016 | high | partial | fix before release | serverInfo.version is empty: pass version=__version__ to MCPServer and test it on the wire. |
| DEP-001 | high | partial | fix before release | Cap pydantic (<3) and httpx (<1); declare uvicorn explicitly with an upper bound; add pip to Dependabot. |
| DRIFT-002 | high | partial | fix before release | The list fallback widens the answer (search ignores query, accommodation ignores stars/amenities/accessible). Report the ignored inputs as a structured field (ignored_parameters), not only in hint, and test the accommodation fallback. |
| DRIFT-004 | high | fail | fix before release | Add live canaries for /status and for the list endpoints of the fallback (/places, /foodEstablishments, /localbusinesses, /civicStructures, /lodgingbusinesses) with the current select. |
| DRIFT-008 | high | fail | planned | Add a suite-wide guard: a conftest hook that fails a live-marked test if the documentation IP pin or test-key is active. |
| FID-002 | high | partial | planned | Web-UI ground truth exists only for list endpoints (zuerich.com vs datasource zht-cms, +8 %). Add one UI-count comparison against /search for the anchor queries. |
| FID-003 | high | partial | fix before release | get_details reports any upstream 4xx as 'Unknown identifier'. Only 404 may say that; other 4xx become degraded with the status named. |
| FID-006 | high | fail | fix before release | Confirm the root paths values/data/facets; a missing root key becomes a structural error (degraded: upstream_shape_changed), never an empty result. |
| FID-007 | high | partial | planned | The list fallback drops rows with missing or invalid geo without counting them; add excluded_without_geo. |
| FID-L02 | high | partial | fix before release | resolve_area ignores missing_facets: a dropped containedInPlace/id facet reads as 'matched no area'. Report it as degraded with the facet named. |
| IDENT-001 | high | not_verified | accepted | not_verified: nothing is published yet (release gate). Source side is clean. Re-run at the first release. |
| IDENT-006 | high | partial | accepted | Not published on purpose: the release waits for discover.swiss's written confirmation of the search entitlement (README Status). |
| IDENT-007 | high | not_verified | accepted | not_verified: no published artefact yet. Re-run at the first release. |
| OBS-001 | high | partial | accepted | An unknown tool is answered as isError result instead of JSON-RPC -32601; this is mcp 2.2.0 MCPServer default behaviour, not server code. Revisit at the next SDK minor. |
| OPS-001 | high | fail | fix before release | Add a source_status live canary and give the live module one shared client and a test timeout. |
| OPS-003 | high | fail | fix before release | Declare the phase (read-only, P4 hardening) and the phase gates P1-P4 plus the release gate in the README. |
| OPS-004 | high | not_verified | accepted | not_verified at audit time by construction: the check judges the audit report, which is written after it. The report of this run follows OPS-004's measured / closed / open split. |
| OPS-005 | high | partial | planned | The copied portfolio scripts (validate_repo.py, check_release_artifacts.py) are format-stable only at line-length 100; shorten the long expressions so they pass at 88-120. |
| OPS-009 | high | partial | planned | Replace the most important of the 43 hand-written upstream payloads with recorded probe responses. |
| OPS-010 | high | fail | fix before release | Mutation TOTAL_BUDGET 25 -> 1e9 survives all 215 tests. Add a real-time budget test, replace the global time.monotonic patch with an own seam, guard the _sleep seam, document the counter-test procedure in CONTRIBUTING. |
| SEC-003 | high | fail | accepted | No OAuth scopes: there is no inbound OAuth. Same reasoning and same condition as SEC-002. |
| SEC-006 | high | partial | planned | README: Claude Desktop configuration example for stdio. |
| SEC-007 | high | fail | accepted | No container is shipped; the server runs as a local stdio process of the user. If a container image is ever published, it gets non-root, read-only FS and dropped capabilities in the same PR. |
| SEC-013 | high | partial | accepted | Key in an environment variable, held as SecretStr, never logged (tested). No secret manager for a local bring-your-own-key tool; the reason goes into SECURITY.md. |
| SEC-018 | high | partial | planned | strict=True on input models and a control-character check on free-text inputs. |
| SEC-021 | high | fail | accepted | Egress is restricted in code (frozenset allow-list, checked on every request and redirect, tested). Network-layer control is the host's business for a local process; SECURITY.md will name the single allowed host and how to change it. |
| SEC-024 | high | fail | fix before release | Wire TransportSecuritySettings with a port-exact host and origin allow-list; SECURITY.md currently describes an allow-list the code does not have. |
| SEC-026 | high | not_verified | accepted | not_verified by the check's own rule: there is no OAuth client registration in this server. |
| SEC-028 | high | fail | fix before release | Split EgressError into a policy block and a resolution failure; retry only the latter, and stop status() from crashing on socket.gaierror. |
| ARCH-002 | medium | partial | planned | Add a 'when to use / not to use' line to the five tools that lack one; separate search from find_accommodation explicitly. |
| ARCH-003 | medium | fail | planned | Empty results already carry a concrete hint; a match_type field and term-based suggestions need upstream support that /search does not offer (no fuzzy flag). Revisit with FID-005. |
| ARCH-008 | medium | fail | planned | Tools-only is deliberate (a tourist question is an action, not a resource); the README will say so in one sentence. |
| ARCH-011 | medium | partial | planned | Split tools.py (2'384 lines) into a tools/ package per tool group. Deferred: pure refactor with tool-hash snapshot as guard, no behaviour change, not a release blocker. |
| ARCH-012 | medium | fail | fix before release | The pinned protocol version is not enforced and the comment in server.py promises a test that does not exist. Add the test against the SDK's LATEST_PROTOCOL_VERSION and correct the comment. |
| ARCH-018 | medium | partial | planned | resultType is set by the SDK; add one wire-format test so an SDK change is noticed. |
| ARCH-020 | medium | fail | planned | Sort tools/list explicitly by name instead of relying on registration order; add a test. |
| ARCH-021 | medium | partial | planned | README: one sentence that the server carries no extensions. |
| ARCH-022 | medium | partial | planned | Move __version__ into a leaf _version.py so client.py does not import the package root. |
| DRIFT-005 | medium | fail | accepted | No scheduled live run: CI deliberately holds no key (bring-your-own-key, 50'000 calls/month on the maintainer's subscription). Live canaries run locally at every phase gate; revisit if a dedicated CI key is issued by discover.swiss. |
| DRIFT-006 | medium | partial | fixed | CHANGELOG claimed an audit report not yet in the repo (now added), said the canaries cover all eight tool paths (six do; get_details and source_status are covered by the fidelity canary and not at all), and README limitation 8 said unknown facet names are always dropped silently (an invented name answers 400). Corrected after the audit. |
| FID-004 | medium | partial | planned | match='all' inherits the upstream default by omitting searchFields; send the explicit field list or pin the default with a live canary (the name/all canary covers half of it). |
| FID-005 | medium | fail | fix before release | Name the query language of searchText and whether operators work (measure first), and remove the empty-result explanations from the find_events and webcams_near descriptions (they belong in hint). Changes the tool hashes. |
| FID-L03 | medium | partial | fix before release | get_details returns a test object (Demo Event) in full and uncounted. Withhold it there too, with excluded_test_objects=1 and a hint. |
| IDENT-002 | medium | partial | planned | Add a test that __version__ equals pyproject.toml and server.json. |
| IDENT-003 | medium | partial | planned | Extend the release check to packages[*].version in server.json. |
| OBS-003 | medium | partial | planned | Emit debug events on the request path (cache hit/miss, fallback step). |
| OBS-007 | medium | partial | planned | Name the attempt count and the endpoint path in the final error after exhausted retries. |
| OBS-008 | medium | partial | planned | Document the readiness marker 'Server lifespan started' in both READMEs. |
| OPS-002 | medium | partial | planned | Add a Mermaid architecture diagram (search-centred, list fallback) to the README; CONTRIBUTING stays English. |
| OPS-007 | medium | partial | planned | Name the supported platforms and add PowerShell equivalents for the env-var examples. |
| OPS-008 | medium | fail | planned | Add tests for validate_repo.py and check_release_artifacts.py; a check that did not run must not report OK. |
| SCALE-010 | medium | partial | planned | README: one sentence that the server emits no change notifications. |
| SDK-003 | medium | partial | planned | ctx.report_progress on the list fallback and on long retry waits. |
| IDENT-004 | low | partial | planned | Enforce badge version against pyproject.toml, not only against the CHANGELOG heading. |

### Re-verification after P5 (2026-09-26)

Targeted re-run of the 27 checks P5 addressed (run
`audits/2026-09-26T121656-Z-discover-swiss-mcp`, target `f326260`), not a full
audit. Live evidence from the maintainer's own runs (24 canaries passed, 1
skipped; query-syntax probe). Result: 10 pass, 16 partial, 1 fail. After the
follow-ups, the live suite on `421f5c6` passed 26 of 26, the demo-event
canary included.

| Check | Before | Re-verified | Follow-up in this change |
|---|---|---|---|
| SEC-003 | fail | pass | — |
| SEC-004 | partial | pass | — |
| SEC-007 | fail | pass | — |
| SEC-016 | partial | pass | — |
| SEC-021 | fail | pass | — |
| ARCH-013 | partial | pass | — |
| ARCH-022 | partial | pass | — |
| DEP-001 | partial | pass | — |
| FID-L02 | partial | pass | — |
| FID-L03 | partial | pass | — |
| SEC-002 | partial | partial | outage → 503 and uncached; `iss` required; identity logged per call |
| SEC-024 | fail | partial | Host check before the metadata; origin wildcards refused; token + foreign Host tested |
| SEC-028 | fail | partial | introspection outage separated from policy block; retry-pair test |
| ARCH-005 | partial | partial | secret out of the repr |
| ARCH-014 | partial | partial | remainder measured after the bucket wait; `Retry-After` header tested |
| OPS-010 | fail | partial | the surviving mutation (header path) now detected; CONTRIBUTING lists survivors |
| FID-005 | fail | fail | measured, stated in the description and the hint |
| FID-006 | fail | partial | rows without `identifier` are a shape error |
| ARCH-012 | fail | partial | open: the SDK accepts older protocol versions; CHANGELOG/README do not name the spec version |
| ARCH-016 | partial | partial | open: no `server/discover` test; SDK default capabilities overstate prompts/resources |
| DRIFT-002 | partial | partial | open: `_schedule_entry` may report another occurrence than the one that matched; `WebLink` as live image unproven |
| DRIFT-004 | fail | partial | the canaries now ran (maintainer, 2026-09-26); open: 404 vs 5xx in `status()` |
| FID-001 | partial | partial | open: recall delta for list `project` and the facet cuts not measured; `explore_area` says nothing when a facet came back full |
| FID-003 | partial | partial | open: transport failures stay results with `degraded`, by design |
| IDENT-002 | partial | partial | open: the version test does not skip in a bare checkout |
| OPS-001 | fail | partial | open: no separate live workflow and no test key (DRIFT-005 accepted) |
| OPS-003 | fail | partial | open: phases are build milestones, not the architecture phases the check names |

Remaining partials of the follow-up rows are listed in the report. The
statuses in the table are those of the re-verification run; the follow-ups
were not re-audited, only tested (each with a counter-test, CONTRIBUTING).

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
