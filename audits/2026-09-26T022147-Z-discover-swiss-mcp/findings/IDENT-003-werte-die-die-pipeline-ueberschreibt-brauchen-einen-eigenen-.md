## Finding: IDENT-003 — Werte, die die Pipeline überschreibt, brauchen einen eigenen Check

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-003` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- packages[*].version is not enforced by CI: counter-test with packages[0].version = 9.9.9 -> validate_repo.py '0 ERROR, 0 WARN', exit 0 (check_release_artifacts.py:124-128 also compares only the top-level version)
- Published side cannot be read back: nothing published to PyPI or the MCP registry yet, and publish.yml has no registry step, so server.json is not shipped by the pipeline

### Expected Behavior

- [ ] `server.json → version` stimmt mit `pyproject.toml` überein
- [ ] **Jeder** `packages[*].version` stimmt überein, nicht nur der erste
- [ ] Ein CI-Check erzwingt das, nicht nur eine Konvention
- [ ] Der Check läuft ohne Projekt-Installation (schlanker Lint-Job genügt)
- [ ] Die Werte, die `publish.yml` zur Laufzeit überschreibt, sind dokumentiert
- [ ] Für jeden überschriebenen Wert existiert ein Check auf die committete Fassung
- [ ] **Und einer auf die geschriebene**: Der publizierte Wert wurde zurückgelesen — Registry gegen Index, oder die Transformation nachvollzogen (Modus 3)
- [ ] Die Transformation erfasst **jedes** Vorkommen des Wertes, nicht nur das erste (`packages[0]` ist kein `packages[*]`)
- [ ] Die Ableitung des Wertes ist gegen Nicht-Tag-Läufe abgesichert: Bei `workflow_dispatch` aus einem Branch ist `GITHUB_REF_NAME` der Branch-Name, und ein blindes `${VAR#v}` schreibt `main` als Version

### Evidence

- server.json:5 version 0.1.0 and server.json:15 packages[0].version 0.1.0 == pyproject.toml:7 0.1.0 (IDENT-003 Modus-1 script: both OK)
- scripts/validate_repo.py:394-402 — CI (ci.yml:70-71) raises ERROR on pyproject vs server.json top-level version drift; stdlib-only script (imports ast/json/re/subprocess/sys/pathlib)
- Counter-test in scratch copy: server.json version -> 9.9.9 gives '[A4] Versionsdrift' and exit 1
- scripts/check_release_artifacts.py:124-143 + publish.yml:38-42 — release gate compares server.json/pyproject and tag vs built version; a workflow_dispatch from a branch makes tag 'main' != version and stops the release
- grep -n "sed -i|jq '\.|yq -i|::set-output|GITHUB_REF_NAME" .github/workflows/ -> only publish.yml:42 (passes the tag to the checker); publish.yml overwrites no committed value

### Gemessen / Geschlossen / Offen

**Gemessen**
- server.json:5 version 0.1.0 and server.json:15 packages[0].version 0.1.0 == pyproject.toml:7 0.1.0 (IDENT-003 Modus-1 script: both OK)
- scripts/validate_repo.py:394-402 — CI (ci.yml:70-71) raises ERROR on pyproject vs server.json top-level version drift; stdlib-only script (imports ast/json/re/subprocess/sys/pathlib)
- Counter-test in scratch copy: server.json version -> 9.9.9 gives '[A4] Versionsdrift' and exit 1
- scripts/check_release_artifacts.py:124-143 + publish.yml:38-42 — release gate compares server.json/pyproject and tag vs built version; a workflow_dispatch from a branch makes tag 'main' != version and stops the release
- grep -n "sed -i|jq '\.|yq -i|::set-output|GITHUB_REF_NAME" .github/workflows/ -> only publish.yml:42 (passes the tag to the checker); publish.yml overwrites no committed value

**Geschlossen**
- Pipeline overwrites nothing, so the 'overwritten value' criteria are vacuous; committed values agree and the top-level field is CI-enforced. The package-entry version is exactly the half-bump case the check warns about and is unguarded.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Genau deshalb kann sie beliebig lange falsch sein. Bei `swiss-environment-mcp` stand sie von v0.2.3 bis v0.5.0 auf einer veralteten Nummer: funktional folgenlos, denn in der Registry landete jedes Mal korrekt die Tag-Version. Aufgefallen ist es niemandem, weil nichts brach.

### Remediation

Extend check_server_json in validate_repo.py (and check_release_artifacts.py) to loop over data.get('packages', []) and error on any packages[i].version != pyproject version.

**Disposition:** Extend the release check to packages[*].version in server.json.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
