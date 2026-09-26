## Finding: IDENT-006 — Veröffentlichte Version ist der aktuelle Stand — kein Release-Gap

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-006` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#31, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Never published (NOT_ON_INDEX): no index version and no release tag
- User-facing work has been unreleased for more than 7 days: 'P1: complete client layer' committed 2026-09-18 (8 days), followed by P2/P3 feature commits
- Release procedure (bump, tag vX.Y.Z, pypi environment approval) is not described in README or CONTRIBUTING; only the release gate condition is

### Expected Behavior

- [ ] Die auf dem Index veröffentlichte Version entspricht dem letzten Release-Tag
- [ ] Kein Release-Tag existiert, den der Index nicht hat (kein fehlgeschlagener Publish)
- [ ] Keine nutzerwirksamen Commits (`fix`, `feat`, `perf`, `revert`) älter als 7 Tage unveröffentlicht
- [ ] `[Unreleased]` im CHANGELOG ist entweder leer oder jünger als die Release-Kadenz — und beschreibt tatsächlich Unveröffentlichtes (`DRIFT-006`)
- [ ] Der Release-Prozess ist im README oder CONTRIBUTING beschrieben, inklusive des manuellen Schritts, falls es einen gibt
- [ ] Der Vergleich hat stattgefunden — Exit `127` der Probe ist `todo`, nicht Pass
- [ ] `IDENT-007` wurde **separat** beantwortet; ein Pass hier wurde nicht als Beleg dafür verbucht

### Evidence

- https://pypi.org/pypi/discover-swiss-mcp/json -> 404, control https://pypi.org/pypi/swiss-culture-mcp/json -> 200 (comparison took place: code NOT_ON_INDEX)
- git tag --list -> 0 tags; git ls-remote --tags origin -> none: no tag missing from the index
- pyproject.toml:7 version 0.1.0; README.md:21-27 'pre-release ... Release | none; version 0.1.0 is not published'; README.md:36-38 release gate = written search confirmation from discover.swiss
- CHANGELOG.md:8-11 — [Unreleased] 'Not released. Release gate: ...' describes exactly the unreleased state
- .github/workflows/publish.yml:5-9 — publish pipeline exists (tag push v*, workflow_dispatch)
- IDENT-007 answered separately (not_verified)

### Gemessen / Geschlossen / Offen

**Gemessen**
- https://pypi.org/pypi/discover-swiss-mcp/json -> 404, control https://pypi.org/pypi/swiss-culture-mcp/json -> 200 (comparison took place: code NOT_ON_INDEX)
- git tag --list -> 0 tags; git ls-remote --tags origin -> none: no tag missing from the index
- pyproject.toml:7 version 0.1.0; README.md:21-27 'pre-release ... Release | none; version 0.1.0 is not published'; README.md:36-38 release gate = written search confirmation from discover.swiss
- CHANGELOG.md:8-11 — [Unreleased] 'Not released. Release gate: ...' describes exactly the unreleased state
- .github/workflows/publish.yml:5-9 — publish pipeline exists (tag push v*, workflow_dispatch)
- IDENT-007 answered separately (not_verified)

**Geschlossen**
- 4 of 7 criteria met. The gap is deliberate and documented (release held until discover.swiss confirms the search entitlement), and the release process is set up rather than missing, so this is NOT_ON_INDEX by design, not a forgotten publish. It stays a finding until the first release.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Das ist eine eigene Fehlerklasse, und die unbequemste der Kategorie: Ein Repository kann grün, auditiert und vollständig korrigiert sein, während jedes `pip install` weiterhin das kaputte Release ausliefert. Nichts widerspricht dem, denn CI testet den Branch, nie das Artefakt. Der Server ist repariert; die Nutzenden merken nichts davon.

### Remediation

Document the release steps (bump pyproject/server.json, CHANGELOG section, tag v0.1.0, approve the pypi environment, verify from the index) in CONTRIBUTING.md; publish as soon as the entitlement gate clears.

**Disposition:** Not published on purpose: the release waits for discover.swiss's written confirmation of the search entitlement (README Status).

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
