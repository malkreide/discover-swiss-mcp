## Finding: IDENT-004 — Dokumentierte Versionen erzwingen — Badges sind sonst dauerhaft falsch

| Feld | Wert |
|---|---|
| **Severity** | low |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-004` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No CI enforcement against pyproject: validate_repo.py C8 compares against the CHANGELOG release heading, is WARN-only, and returns silently when there is none (scripts/validate_repo.py:566-576); counter-test with README.de.md badge 0.0.9 -> '0 ERROR, 0 WARN', exit 0
- Hence no counter-test where a reverted badge breaks the check with exit 1

### Expected Behavior

- [ ] Jedes Versions-Badge stimmt mit `pyproject.toml` überein
- [ ] Alle README-Varianten geprüft (EN **und** DE), nicht nur die englische
- [ ] Ein CI-Check erzwingt das im selben Lauf wie IDENT-003
- [ ] Gegenprobe gefahren: zurückgedrehtes Badge bricht den Check mit `exit 1`

### Evidence

- README.md:7 and README.de.md:5 — shields badge version-0.1.0 == pyproject.toml:7 (check script: both OK; control pattern extracts 0.0.9 from a test badge)

### Gemessen / Geschlossen / Offen

**Gemessen**
- README.md:7 and README.de.md:5 — shields badge version-0.1.0 == pyproject.toml:7 (check script: both OK; control pattern extracts 0.0.9 from a test badge)

**Geschlossen**
- 2 of 4 criteria met: both badges are currently correct and both READMEs were checked, but nothing enforces it; pre-release the existing gate cannot fire.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Das Versions-Badge im README ist die Zahl, die Menschen als Erstes sehen — und die einzige Stelle im ganzen Repo, hinter der **nichts** steht. `publish.yml` synchronisiert das Manifest aus dem Tag, Tests prüfen den Code, aber ein Shields.io-Badge korrigiert niemand automatisch.

### Remediation

Compare README badges against pyproject version inside check_server_json (same run as the server.json check) and report ERROR; verify with a reverted badge.

**Disposition:** Enforce badge version against pyproject.toml, not only against the CHANGELOG heading.

### Effort Estimate

XS

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
