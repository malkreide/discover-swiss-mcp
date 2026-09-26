## Finding: OPS-008 — Prüflogik in Workflow-Heredocs ist nicht nachweisbar

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-008` |
| **PDF-Reference** | Custom (Portfolio-Fundstück mcp-audit-skill#81, 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- The two extracted guards that decide red/green have no tests: grep -rl 'validate_repo|check_release_artifacts' tests/ -> no hit
- State set incomplete: validate_repo.py C8 returns silently when CHANGELOG has no release heading (scripts/validate_repo.py:566-576); counter-test with a detuned badge -> exit 0, no warning
- No documented mutation counter-test for the guards

### Expected Behavior

_(siehe Check-Definition)_

### Evidence

- grep -c "<<" .github/workflows/*.yml -> 0 for ci.yml and publish.yml; control "python - <<'PY'" matches -> no heredoc guard in any workflow
- .github/workflows/ci.yml:70-71, publish.yml:38-42 — judging logic lives in scripts/validate_repo.py and scripts/check_release_artifacts.py, called by exit code
- tests/test_server.py:88-95,148-154 — scripts/gen_tool_hashes.py is loaded and exercised by a test

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep -c "<<" .github/workflows/*.yml -> 0 for ci.yml and publish.yml; control "python - <<'PY'" matches -> no heredoc guard in any workflow
- .github/workflows/ci.yml:70-71, publish.yml:38-42 — judging logic lives in scripts/validate_repo.py and scripts/check_release_artifacts.py, called by exit code
- tests/test_server.py:88-95,148-154 — scripts/gen_tool_hashes.py is loaded and exercised by a test

**Geschlossen**
- 2 of 5 criteria met. The core rule (no judging heredocs in workflows) holds, but the extracted guards are untested and one of them collapses 'not checked' into 'OK'.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Prüflogik in einem Workflow-Heredoc — `run: |` gefolgt von `python - <<'PY' … PY` — ist ausführbarer Code an der einzigen Stelle im Repo, an der Code keine Tests haben kann. Er lässt sich nicht importieren, nicht mit Grenzfällen aufrufen, nicht mutationstesten. Er wird genau einmal geschrieben, in dem Moment, in dem der Autor sicher ist, dass er stimmt, und danach nie wieder befragt.

### Remediation

Add tests/test_scripts.py covering validate_repo.py (server.json drift -> ERROR, badge drift, missing release heading -> explicit 'not checked') and check_release_artifacts.py (tag mismatch, missing marker, description > 100), each run once against a deliberately broken input.

**Disposition:** Add tests for validate_repo.py and check_release_artifacts.py; a check that did not run must not report OK.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
