## Finding: ARCH-018 — resultType auf allen Results — «complete» ist kein Default, den man weglässt

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-018` |
| **PDF-Reference** | SEP-2322 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No test checks resultType on the wire (grep tests/ → 0); it rests entirely on SDK behaviour

### Expected Behavior

- [ ] `resultType` liegt auf jedem Result an — Erfolgs- **und** Fehlerpfad
- [ ] Der Wert ist `"complete"`, solange der Server kein MRTR führt
- [ ] Wird MRTR geführt, ist `"input_required"` ausschliesslich dem Zwischenstand vorbehalten (`HITL-006`)
- [ ] Stammt das Feld aus dem SDK, ist dessen Mindestversion im Manifest gepinnt
- [ ] Ein Test prüft das Feld am tatsächlichen Wire-Format, nicht am Rückgabewert der Python-Funktion — dazwischen liegt die Serialisierung, und genau dort geht es verloren

### Evidence

- runtime HTTP tools/call search without key (error path): result.isError true, resultType 'complete'
- runtime stdio tools/call source_status (success path): resultType 'complete', structuredContent present
- runtime: tools/list, server/discover, resources/list, prompts/list, resources/templates/list all carry resultType 'complete'
- grep resultType|result_type src/ → 0: field set by SDK (mcp 2.2.0); pyproject.toml:34 mcp>=2,<3

### Gemessen / Geschlossen / Offen

**Gemessen**
- runtime HTTP tools/call search without key (error path): result.isError true, resultType 'complete'
- runtime stdio tools/call source_status (success path): resultType 'complete', structuredContent present
- runtime: tools/list, server/discover, resources/list, prompts/list, resources/templates/list all carry resultType 'complete'
- grep resultType|result_type src/ → 0: field set by SDK (mcp 2.2.0); pyproject.toml:34 mcp>=2,<3

**Geschlossen**
- Field present on success and error paths via the SDK, value 'complete', no MRTR. Only the wire-format regression test is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Seit `2026-07-28` trägt **jedes** Result ein Pflichtfeld `resultType`, mit genau zwei Werten: `"complete"` für ein fertiges Ergebnis und `"input_required"` für den Zwischenstand eines Multi-Round-Trip-Requests (`HITL-006`).

### Remediation

Add a test using mcp.Client (or raw JSON-RPC over stdio) that asserts resultType == 'complete' on a successful and an isError tool result.

**Disposition:** resultType is set by the SDK; add one wire-format test so an SDK change is noticed.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-018` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
