## Finding: OPS-005 — Pipeline unterscheidet «bestanden» von «nicht gelaufen»

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-005` |
| **PDF-Reference** | Custom (Portfolio-Fundstück mcp-continuous-auditor#29) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Copied portfolio scripts are only format-stable at the local line-length 100: ruff format --check --line-length {88,110,120} scripts/ fails for validate_repo.py, check_release_artifacts.py, gen_tool_hashes.py, p2/p3 run scripts; no CI step enforces multi-width stability
- validate_repo.py C8 version-anchor check is silent without a release heading (scripts/validate_repo.py:566-576): 'not checked' collapses into 'OK'. Counter-test in a scratch copy: README.de.md badge set to 0.0.9 -> '0 ERROR, 0 WARN', exit 0
- No in-repo evidence that gates were verified in both directions (no documented counter-test)

### Expected Behavior

- [ ] Mindestens ein committeter Workflow führt die Testsuite aus, ausgelöst durch `push` und `pull_request` — nicht nur als `.template` für andere Repos
- [ ] Jeder Schritt mit `continue-on-error`, bedingtem `if:` oder `|| true` hat eine **sichtbare Folge**, wenn er ausbleibt: eine Zeile im Bericht, ein Artefakt, eine Annotation
- [ ] Kein Test wird wegen einer fehlenden Abhängigkeit übersprungen, die CI installieren könnte
- [ ] `run:`-Blöcke mit Pipes setzen `pipefail`, sonst maskiert der letzte Befehl den Exit-Code
- [ ] Jedes Gate ist in beide Richtungen verifiziert: Es schlägt an, wenn es soll, und schweigt, wenn es soll
- [ ] Ein Artefakt, das zwischen Repos kopiert wird, ist gegen **jede** dort genutzte Werkzeug-Konfiguration geprüft — nicht nur gegen die lokale
- [ ] Linter und Formatter laufen über **alle** Verzeichnisse mit eigenem Code — insbesondere über `scripts/`, wo die Prüfskripte der übrigen Gates liegen
- [ ] Jeder konfigurierte Regelsatz wird von mindestens einem Workflow auch aufgerufen
- [ ] Kein Gate ist per Kommentar stillgelegt; wo es sein muss, existiert stattdessen ein verfolgbarer Eintrag
- [ ] Der Bericht unterscheidet «kein Befund» von «nicht geprüft»

### Evidence

- .github/workflows/ci.yml:3-7, 53-71 — committed workflow on push+pull_request runs ruff check ., ruff format --check ., pytest -m 'not live', validate_repo.py
- grep -nE 'continue-on-error|if:\s|\|\| true' .github/workflows/*.yml -> no hit (exit 1); control line matches
- Pipe grep only hits YAML block scalars 'run: |' (publish.yml:30,39); their bodies contain no shell pipes
- grep for commented-out gates (deaktiviert|disabled|TODO|vorerst) in workflows -> no hit
- ruff check . / ruff format --check . cover src, tests, scripts; probes/ excluded with rationale (pyproject.toml:78-83); lint select pinned (pyproject.toml:92-97)
- runtime: pytest -q -rs -> 215 passed, 18 skipped, all skips 'DISCOVER_SWISS_KEY is not set' in test_live.py (credential, not dependency; CI deselects them)

### Gemessen / Geschlossen / Offen

**Gemessen**
- .github/workflows/ci.yml:3-7, 53-71 — committed workflow on push+pull_request runs ruff check ., ruff format --check ., pytest -m 'not live', validate_repo.py
- grep -nE 'continue-on-error|if:\s|\|\| true' .github/workflows/*.yml -> no hit (exit 1); control line matches
- Pipe grep only hits YAML block scalars 'run: |' (publish.yml:30,39); their bodies contain no shell pipes
- grep for commented-out gates (deaktiviert|disabled|TODO|vorerst) in workflows -> no hit
- ruff check . / ruff format --check . cover src, tests, scripts; probes/ excluded with rationale (pyproject.toml:78-83); lint select pinned (pyproject.toml:92-97)
- runtime: pytest -q -rs -> 215 passed, 18 skipped, all skips 'DISCOVER_SWISS_KEY is not set' in test_live.py (credential, not dependency; CI deselects them)

**Geschlossen**
- 7 of 10 criteria met. Pipeline runs everything on push/PR with no silent-failure constructs; gaps are width-scoped copies, a gate that cannot fire pre-release, and undocumented gate counter-tests.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Check, der nicht gelaufen ist, sieht in jeder Zusammenfassung exakt aus wie einer, der bestanden hat. Grüner Haken, keine Meldung, weiter. Das ist keine Nachlässigkeit im Einzelfall, sondern eine Eigenschaft der Werkzeuge: CI-Oberflächen zeigen Fehlschläge, nicht Abwesenheiten.

### Remediation

Add a CI step looping ruff format --check --line-length 88/100/110/120 over the copied scripts (after reformatting them to a width-stable form), make C8 emit INFO 'not checked: no release heading' instead of returning silently, and record gate counter-tests in CONTRIBUTING.

**Disposition:** The copied portfolio scripts (validate_repo.py, check_release_artifacts.py) are format-stable only at line-length 100; shorten the long expressions so they pass at 88-120.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
