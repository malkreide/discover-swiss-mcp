## Finding: ARCH-021 — Extensions deklariert und versioniert — Tasks sind kein Kern-Feature mehr

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-021` |
| **PDF-Reference** | SEP-2663 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README.md / README.de.md do not state that the server carries no extensions (grep -i extension → 0; control: 21 hits in ARCH-021.md)

### Expected Behavior

- [ ] Führt der Server keine Extension, ist das im README in einem Satz festgehalten — nicht bloss unerwähnt
- [ ] Jede geführte Extension erscheint mit vollständiger, versionierter Kennung (`io.modelcontextprotocol/tasks`) in den Server-Capabilities
- [ ] Die Deklaration deckt sich in **beide** Richtungen mit dem Code
- [ ] Bei Tasks: Der Server spricht die Extension-Fassung (`tasks/get` / `tasks/update`), nicht `tasks/result` oder `tasks/list`
- [ ] Bei Tasks: Das README sagt, ob unaufgeforderte Task-Handles zurückgegeben werden, und die Tool-Descriptions sagen es bei den betroffenen Tools
- [ ] Eigene, nicht-offizielle Erweiterungen laufen unter einem eigenen Namensraum, nie unter `io.modelcontextprotocol/*`

### Evidence

- grep 'io.modelcontextprotocol/|extensions' src/ → only src/discover_swiss_mcp/net.py:144 (httpx request extensions={'sni_hostname': host}, not MCP) (control: hits .venv/.../mcp/shared/subscriptions.py)
- grep 'tasks/(get|update|result|list)|TaskHandle|task_id' src/ → 0 (control: hits .venv/.../mcp_types/_v2025_11_25/__init__.py)
- runtime server/discover capabilities: no extensions declared — declaration matches code in both directions

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep 'io.modelcontextprotocol/|extensions' src/ → only src/discover_swiss_mcp/net.py:144 (httpx request extensions={'sni_hostname': host}, not MCP) (control: hits .venv/.../mcp/shared/subscriptions.py)
- grep 'tasks/(get|update|result|list)|TaskHandle|task_id' src/ → 0 (control: hits .venv/.../mcp_types/_v2025_11_25/__init__.py)
- runtime server/discover capabilities: no extensions declared — declaration matches code in both directions

**Geschlossen**
- No extensions, no Tasks, no own namespace under io.modelcontextprotocol; only the one-sentence README statement is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der erste Umzugskandidat ist **Tasks**. In `2025-11-25` waren sie experimenteller Teil des Kerns; jetzt sind sie `io.modelcontextprotocol/tasks` — und die Extension ist nicht dieselbe API:

### Remediation

Add to README.md and README.de.md (e.g. in a 'MCP Protocol Version' section): 'This server speaks 2026-07-28 and carries no extensions.'

**Disposition:** README: one sentence that the server carries no extensions.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-021` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
