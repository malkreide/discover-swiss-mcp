## Finding: OPS-003 — Phasenarchitektur: Read-only First, dann Write, dann Multi-Agent

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-003` |
| **PDF-Reference** | Anhang C4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No phase declaration: grep -iE 'phase|roadmap|read.only.first' over README.md, README.de.md, CHANGELOG.md, docs/*.md -> no hit (control 'Phase 1' matches). The P1-P4 labels in commits/CHANGELOG are build milestones, not OPS-003 phases
- No roadmap file (find for *phase*/*roadmap* outside .venv -> none)
- No documented phase-transition prerequisites (audit run, ISDS, DSG record)
- Phase transitions not recorded in CHANGELOG

### Expected Behavior

- [ ] Aktuelle Phase explizit im README deklariert (Phase 1 / 2 / 3)
- [ ] Phase entspricht den tatsächlichen Tool-Annotations (kein Phase-1-Server mit destruktiven Tools)
- [ ] Roadmap-File mit phasenspezifischen Tasks vorhanden
- [ ] Phase-Übergang erfordert dokumentierte Voraussetzungen:
  - Phase 1 → 2: Audit-Run, ISDS, DSG-Verarbeitungsverzeichnis abgeschlossen
  - Phase 2 → 3: Semantic Layer, Identity-Resolution, GL-Sign-off, Datenschutzbeauftragte:r-Sign-off
- [ ] Phase-Übergänge im CHANGELOG dokumentiert (Synergie zu ARCH-012)

### Evidence

- src/discover_swiss_mcp/server.py:170-179 — all 8 tools annotated readOnlyHint=True, destructiveHint=False
- tests/test_server.py:103-108 — test asserts read_only_hint True / destructive_hint False for every tool
- grep -rnE 'destructiveHint.*True' src/ -> no hit

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:170-179 — all 8 tools annotated readOnlyHint=True, destructiveHint=False
- tests/test_server.py:103-108 — test asserts read_only_hint True / destructive_hint False for every tool
- grep -rnE 'destructiveHint.*True' src/ -> no hit

**Geschlossen**
- 1 of 5 criteria met: the server is de facto Phase 1 (read-only, verified), but the phase is not declared and there is no roadmap or gate.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Anhang sagt klar: «Die häufigste Ursache von MCP-Sicherheitsvorfällen 2025/26 war: ‹Wir haben gleich Schreibzugriffe gebaut, weil es ging.›»

### Remediation

Add a '## Phase' section to both READMEs ('Phase 1: read-only wrapper' with status table) and docs/roadmap.md listing Phase 1 completion items and Phase 2/3 prerequisites; note the declaration in CHANGELOG.

**Disposition:** Declare the phase (read-only, P4 hardening) and the phase gates P1-P4 plus the release gate in the README.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
