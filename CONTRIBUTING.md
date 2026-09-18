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

Run all four before pushing. A green `ruff check` is not evidence of a green
format gate — they are separate checks, and `ruff` is pinned exactly in the
`dev` extra so the local version matches CI.

Tests marked `live` hit the real API and need `DISCOVER_SWISS_KEY`. CI never
runs them.

## Commits and pull requests

- Conventional Commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- Add an entry under `[Unreleased]` in `CHANGELOG.md`.
- Open pull requests as drafts; never push directly to `main`.
- No push without a secrets check. `DISCOVER_SWISS_KEY` never goes into a file
  that gets committed.
