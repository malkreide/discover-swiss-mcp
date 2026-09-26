# Contributing

Thanks for considering a contribution.

## Ground rules

- **Swiss German orthography** in German text: no `ß`, guillemets «».
- **Code, docstrings and tool descriptions are English.** The README is
  bilingual: `README.md` (English, primary) and `README.de.md`.
- **Every tool is read-only** (`readOnlyHint: true`, `openWorldHint: true`) and
  has a testable `*_impl` function separate from the MCP wrapper. Maximum 15
  tools per server; this one plans 8.
- **Every response is the Pydantic envelope** with `source`, `provenance`,
  `retrieved_at`, `source_freshness` and `degraded`. Attribution belongs in the
  response, never only in the README.
- **The probe is the truth.** `probes/` holds the recorded responses of the
  live probe. The vendor documentation is demonstrably wrong in several places
  (search entitlement, paging field names, example project). Where they
  disagree, the recorded response wins — and the disagreement gets written
  down.
- **Data fidelity.** Send scope parameters explicitly. An empty result carries
  a concrete `hint`. No tool description explains away or apologises for an
  empty result. Query syntax and matching granularity belong in the tool
  description, not in the README.

## Development

```bash
pip install -e ".[dev]"

pytest -m "not live"      # what CI runs, no network
ruff check .
ruff format --check .
python scripts/validate_repo.py .
```

On Windows PowerShell the commands are the same; set variables with
`$env:DISCOVER_SWISS_KEY = "..."` instead of `export`.

Run all four before pushing. A green `ruff check` is not evidence of a green
format gate — they are separate checks, and `ruff` is pinned exactly in the
`dev` extra so the local version matches CI.

Tests marked `live` hit the real API and need `DISCOVER_SWISS_KEY`. CI never
runs them. Run `pytest -m live -rA` at every phase gate; `-rA` prints each
measured value next to its floor.

## Counter-tests: a guard that cannot fail is not a guard

A test suite shows that the code does what the tests expect. It does not show
that the tests would notice if it stopped. That second question is answered by
breaking the code on purpose and watching a test turn red — a counter-test.
The audit of 2026-09-26 found the gap this closes: setting the whole-call time
budget to `1e9` left all 215 tests green (audit OPS-010).

**Procedure.** For a central assurance:

1. Break it in the smallest way that should matter (flip the condition, widen
   the constant, drop the call). Do it on a working copy you will discard.
2. Run `pytest -m "not live"`. At least one test must fail, and it should be
   the test named below.
3. Restore the code and run the suite again — green.
4. If nothing failed, the assurance is untested: write the test first, then
   repeat. A mutation that survives is a finding, not noise.

Time is controlled through the client's own seams, `client._sleep` and
`client._monotonic` — never by patching `asyncio.sleep` or `time.monotonic`,
which would change every caller in the process, the event loop included.
`test_the_sleep_fixture_does_not_silence_real_sleep` and
`test_the_time_seams_default_to_the_real_clock` guard the seams; at least one
test per wall-clock assurance runs on the real clock
(`test_the_budget_holds_under_real_time`).

**Assurances and the tests that must turn red.** Last run on 2026-09-26. A
mutation that survived is recorded under «Survivors» below with what closed it —
the list is never shortened to look clean.

| Assurance | Mutation | Tests that fail |
|---|---|---|
| Whole-call time budget | `deadline = now + 1e9` | `test_the_budget_holds_under_real_time`, among 3 failing |
| IPv4-mapped / 6to4 addresses are blocked | skip the unwrapping | `test_embedded_and_special_addresses_are_blocked` (2) |
| OAuth: token must be for this resource | drop the audience check | `test_tokens_not_for_this_resource_are_refused` (2) |
| OAuth: scopes are checked per call | skip the scope comparison | `test_too_few_scopes_is_403_naming_the_missing_scope` |
| Host check is port-exact | loopback list `127.0.0.1:*` | `test_foreign_host_port_or_origin_is_refused`, among 3 failing |
| `serverInfo.version` is set | `version=""` | `test_server_info_carries_the_version_on_the_wire` |
| A moved root key is not an empty result | accept `count > 0` without rows | 3 failing in `tests/test_shape.py` |
| Only an invalid id or a 404 is «unknown» | catch every upstream 4xx | `test_an_upstream_400_is_not_reported_as_unknown_identifier`, among 3 failing |
| Container keeps its hardening | `readOnlyRootFilesystem: false` | `test_container_security_context` |
| Egress policy names exactly the allowed hosts | add or drop a Cilium FQDN | `test_cilium_policy_names_exactly_the_allowed_hosts` |
| Budget left after a bucket wait | reuse the pre-wait `remaining` | `test_the_request_gets_only_what_the_bucket_wait_left_of_the_budget` |
| `Retry-After` header is read | ignore the header | `test_429_reads_retry_after_from_the_header_when_the_body_names_none` |
| DNS failure retried, policy block not | — (pair asserted together) | `test_a_dns_failure_is_retried_but_an_egress_block_is_not` |
| Introspection outage is not «invalid» | return `None` on a non-200 | `test_an_unreachable_authorization_server_lets_nothing_through`, `test_an_outage_is_not_cached_so_a_valid_token_works_after_recovery` |
| `iss` is required | accept a missing `iss` | `test_an_answer_without_issuer_is_refused` |
| Host check precedes the metadata | skip the Host check in the gate | `test_a_foreign_host_is_refused_before_metadata_or_token` (2), among 3 failing |
| Rows without `identifier` are a shape error | drop the check | 4 failing in `tests/test_shape.py` |
| Unsupported query syntax is named in the hint | drop the note | `test_an_empty_result_after_unsupported_syntax_names_the_syntax` (7) |

**Survivors.**

| Found | Mutation | Closed by |
|---|---|---|
| Re-verification 2026-09-26 (M20) | ignore the `Retry-After` header | `test_429_reads_retry_after_from_the_header_when_the_body_names_none` |
| Re-verification 2026-09-26 | reuse the pre-wait `remaining` (visible only under real time) | `test_the_request_gets_only_what_the_bucket_wait_left_of_the_budget` |

## Commits and pull requests

- Conventional Commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- Add an entry under `[Unreleased]` in `CHANGELOG.md`.
- Open pull requests as drafts; never push directly to `main`.
- No push without a secrets check. `DISCOVER_SWISS_KEY` never goes into a file
  that gets committed.
