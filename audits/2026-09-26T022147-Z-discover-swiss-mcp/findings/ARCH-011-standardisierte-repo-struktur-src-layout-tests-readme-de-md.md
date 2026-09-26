## Finding: ARCH-011 — Standardisierte Repo-Struktur (src-Layout, tests, README.de.md)

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-011` |
| **PDF-Reference** | Anhang A8 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- >5 tools but no tools/ directory with file-per-group split; tools.py is 2384 lines and server.py 374 lines (>200)
- Deviation from the standard layout is not justified in README.md or README.de.md
- CI workflow is named ci.yml instead of test.yml (functionally equivalent; noted only)

### Expected Behavior

- [ ] Top-Level-Pflicht-Files vorhanden: `README.md`, `README.de.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`
- [ ] Verzeichnisse vorhanden: `src/`, `tests/`, `.github/workflows/`
- [ ] `src/`-Layout korrekt (kein flat package)
- [ ] CI-Workflows: mindestens `test.yml` (CI ohne live-Tests) und `publish.yml`
- [ ] `README.de.md` ist parallel zu `README.md` (gleiche Top-Level-Sektionen)
- [ ] Bei > 5 Tools: `tools/`-Verzeichnis mit File-pro-Gruppe-Aufteilung
- [ ] Abweichungen vom Standard sind in `README.md` **oder** `README.de.md` begründet — eine Begründung ausschliesslich in `SECURITY.md`, `CONTRIBUTING.md`, `docs/`, einem Issue oder einer Commit-Message zählt nicht

### Evidence

- top level: README.md, README.de.md, CHANGELOG.md, LICENSE, pyproject.toml all present; src/, tests/, .github/workflows/ (ci.yml, publish.yml) present
- pyproject.toml:66-67 — [tool.hatch.build.targets.wheel] packages = ['src/discover_swiss_mcp'] (src layout)
- .github/workflows/ci.yml:66-67 — pytest -m "not live"; .github/workflows/publish.yml present
- README.md vs README.de.md '^## ' headings: 20 each, same order, semantically matching (e.g. Anchor demo queries/Anker-Abfragen, Known limitations/Bekannte Einschränkungen)
- src/discover_swiss_mcp/tools.py (2384 lines) holds all eight *_impl; src/discover_swiss_mcp/server.py is 374 lines; no tools/ package
- README.md:254-274 — Project Structure lists tools.py but gives no reason for deviating from a tools/ package

### Gemessen / Geschlossen / Offen

**Gemessen**
- top level: README.md, README.de.md, CHANGELOG.md, LICENSE, pyproject.toml all present; src/, tests/, .github/workflows/ (ci.yml, publish.yml) present
- pyproject.toml:66-67 — [tool.hatch.build.targets.wheel] packages = ['src/discover_swiss_mcp'] (src layout)
- .github/workflows/ci.yml:66-67 — pytest -m "not live"; .github/workflows/publish.yml present
- README.md vs README.de.md '^## ' headings: 20 each, same order, semantically matching (e.g. Anchor demo queries/Anker-Abfragen, Known limitations/Bekannte Einschränkungen)
- src/discover_swiss_mcp/tools.py (2384 lines) holds all eight *_impl; src/discover_swiss_mcp/server.py is 374 lines; no tools/ package
- README.md:254-274 — Project Structure lists tools.py but gives no reason for deviating from a tools/ package

**Geschlossen**
- Files, directories, src layout, CI and bilingual parity are fine; the tool-module split and the README justification for the deviation are missing (5 of 7 criteria).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Aus dem Schweizer Public-Data-Portfolio bewährt sich ein konsistentes Repo-Layout. Das ist nicht nur Code-Schönheit — es ist Operational Discipline:

### Remediation

Either split tools.py into src/discover_swiss_mcp/tools/ (search.py, lodging.py, tours.py, events.py, webcams.py, area.py, status.py) or add a sentence in README.md and README.de.md 'Project Structure' explaining why a single tools.py was kept.

**Disposition:** Split tools.py (2'384 lines) into a tools/ package per tool group. Deferred: pure refactor with tool-hash snapshot as guard, no behaviour change, not a release blocker.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-011` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
