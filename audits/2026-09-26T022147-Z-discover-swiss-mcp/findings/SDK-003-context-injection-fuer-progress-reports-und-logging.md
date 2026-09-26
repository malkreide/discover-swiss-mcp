## Finding: SDK-003 — Context Injection für Progress Reports und Logging

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SDK-003` |
| **PDF-Reference** | Sec 3.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No ctx.report_progress on paths that can exceed 2 s: list fallback up to FALLBACK_MAX_CALLS sequential calls (tools.py:846-871), retry ladder/429 waits up to 25–55 s (client.py:248,772)
- No test demonstrating that no notifications/message is emitted for a request without logLevel (trivially true today, not held by a test)

### Expected Behavior

- [ ] Tools mit voraussichtlicher Laufzeit > 2s haben `ctx: Context`-Parameter
- [ ] Lang laufende Tools rufen `ctx.report_progress()` mindestens alle 1–2 Sekunden
- [ ] Fehlerfälle, die nicht direkt Tool-Result werden, werden via `ctx.warning()` / `ctx.error()` geloggt (nicht stumm geschluckt)
- [ ] Bei schreibenden Tools (HITL-005): `ctx.elicit()` für Bestätigung verwendet
- [ ] Logger-Statements im Code-Body nutzen `ctx.info()`, nicht direkt `print()` oder Stdlib-`logger` (für stdio-Server kritisch — siehe OBS-004)
- [ ] Auf `2026-07-28`: kein `logging/setLevel`-Handler mehr; der Level kommt aus `io.modelcontextprotocol/logLevel` in `_meta`
- [ ] Auf `2026-07-28`: `notifications/message` wird ausschliesslich für Requests gesendet, die das `logLevel`-Feld trugen — mit einem Test belegt, der einen Request **ohne** das Feld stellt und prüft, dass keine Meldung kommt
- [ ] Auf `2026-07-28`: Der Ausstieg aus dem Logging-Feature hat ein Datum (`ARCH-019`), und der Zielzustand ist `stderr` oder OTel — nicht Stille

### Evidence

- src/discover_swiss_mcp/server.py:231,246,261,276,291,306,321,336 — every tool declares ctx: Context
- src/discover_swiss_mcp/server.py:200-222 — failures logged (log.exception) to stderr and raised as masked ToolError, not swallowed; logging_config.py:32,48 stderr
- grep 'report_progress' src/ → 0; grep 'ctx.(info|warning|error)' src/ → 0 (control: pattern hits .venv/.../mcp/server/mcpserver/context.py)
- runtime: logging/setLevel → -32601 (no handler); server never sends notifications/message (no ctx logging calls)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:231,246,261,276,291,306,321,336 — every tool declares ctx: Context
- src/discover_swiss_mcp/server.py:200-222 — failures logged (log.exception) to stderr and raised as masked ToolError, not swallowed; logging_config.py:32,48 stderr
- grep 'report_progress' src/ → 0; grep 'ctx.(info|warning|error)' src/ → 0 (control: pattern hits .venv/.../mcp/server/mcpserver/context.py)
- runtime: logging/setLevel → -32601 (no handler); server never sends notifications/message (no ctx logging calls)

**Geschlossen**
- Context is injected everywhere and logging correctly targets stderr per the 2026-07-28 baseline; progress reporting for the long fallback/retry paths is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: FastMCP bietet via `Context`-Parameter ein typsicheres Interface zu Server-Internals: Logging, Progress-Reports, Client-Info, Session-State, Sampling, Elicitation. Tools, die `ctx: Context` als Parameter deklarieren, bekommen dieses Objekt automatisch injiziert (Dependency Injection durch FastMCP).

### Remediation

Pass ctx into the fallback scan / retry waits and call await ctx.report_progress(i, total, message) per list page and before each retry sleep.

**Disposition:** ctx.report_progress on the list fallback and on long retry waits.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SDK-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
