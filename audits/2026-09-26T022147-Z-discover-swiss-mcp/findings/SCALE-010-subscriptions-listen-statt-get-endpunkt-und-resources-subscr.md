## Finding: SCALE-010 — subscriptions/listen statt GET-Endpunkt und resources/subscribe

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SCALE-010` |
| **PDF-Reference** | SEP-2575 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README does not state that the server emits no change notifications (criterion 1 requires one sentence, not silence)
- The SDK's backward-compatible 2025-11-25 session path still serves a server-initiated GET stream: after a legacy initialize, GET /mcp with mcp-session-id → 200 text/event-stream (runtime). Modern GET is 405; the legacy stream is SDK compat behaviour, not server code

### Expected Behavior

- [ ] Führt der Server keine Änderungsbenachrichtigungen, ist das belegt und im README festgehalten — mit einem Satz, nicht durch Schweigen
- [ ] Kein `resources/subscribe` / `resources/unsubscribe` mehr im Code
- [ ] Kein GET-Endpunkt für serverinitiierte Nachrichten; ein GET auf den MCP-Pfad antwortet `405`
- [ ] Führt der Server Benachrichtigungen: Der Client trägt sich über `subscriptions/listen` je Typ ein, und der Server bestätigt
- [ ] Jede Benachrichtigung trägt `io.modelcontextprotocol/subscriptionId`
- [ ] `notifications/progress` und `notifications/message` laufen weiter auf dem Antwortstrom ihres Requests, **nicht** auf `subscriptions/listen` — mit einem Test belegt
- [ ] Der Reverse Proxy puffert den langlebigen Strom nicht und schliesst ihn nicht vor dem Server

### Evidence

- src/ — grep 'resources/(un)?subscribe|subscriptions/listen|subscriptionId|toolsListChanged|notifications/progress|report_progress|ctx\.info|list_changed' → no hit (control fires on 3 control lines)
- runtime (audit): initialize (2025-11-25) response capabilities tools.listChanged=false, prompts.listChanged=false, resources.listChanged=false, resources.subscribe=false
- runtime (audit): resources/subscribe → -32601 Method not found
- runtime (audit): GET /mcp with MCP-Protocol-Version 2026-07-28 → 405, Allow: POST

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/ — grep 'resources/(un)?subscribe|subscriptions/listen|subscriptionId|toolsListChanged|notifications/progress|report_progress|ctx\.info|list_changed' → no hit (control fires on 3 control lines)
- runtime (audit): initialize (2025-11-25) response capabilities tools.listChanged=false, prompts.listChanged=false, resources.listChanged=false, resources.subscribe=false
- runtime (audit): resources/subscribe → -32601 Method not found
- runtime (audit): GET /mcp with MCP-Protocol-Version 2026-07-28 → 405, Allow: POST

**Geschlossen**
- The server has no notification or subscription mechanism (code grep with control, capabilities, Method-not-found) and the modern GET answers 405. The README is silent on notifications and the legacy-era GET stream remains reachable for 2025-11-25 clients → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Die Trennlinie, an der die Migration schiefgeht:** Nicht alles, was der Server ungefragt sendet, gehört in diesen Strom. Request-bezogene Benachrichtigungen — `notifications/progress`, `notifications/message` — laufen weiterhin auf dem Antwortstrom **des Requests, zu dem sie gehören**. Nur was keinem Request zugeordnet ist, gehört auf `subscriptions/listen`.

### Remediation

Add one README sentence under the protocol/transport section: 'This server sends no list-changed or resource notifications; tools are static.' Optionally note that legacy (2025-11-25) sessions still get the SDK's GET stream, or disable legacy protocol support if only 2026-07-28 clients are targeted.

**Disposition:** README: one sentence that the server emits no change notifications.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SCALE-010` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
