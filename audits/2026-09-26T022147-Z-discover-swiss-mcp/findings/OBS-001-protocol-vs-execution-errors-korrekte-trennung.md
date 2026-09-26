## Finding: OBS-001 — Protocol vs. Execution Errors: korrekte Trennung

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-001` |
| **PDF-Reference** | Sec 6.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Unknown tool is answered as a tool result with isError=true instead of a JSON-RPC protocol error (-32601); this is mcp 2.2.0 MCPServer behaviour (exceptions.py docstring: SDK raises ToolError for unknown tool names), but the server does not override it — pass criterion 'standardised codes for protocol-level errors' not met
- No test covers the protocol-error path (unknown tool); grep for no_such_tool/unknown tool/-32601 in tests/ returns nothing
- Upstream-unreachable/quota states are returned as isError=false results with degraded+hint rather than isError=true; model-actionable, but deviates from the check's table (API down -> isError:true)

### Expected Behavior

- [ ] Tool-Handler fangen anwendungsspezifische Fehler (FileNotFound, RateLimit, InvalidArgument) ab
- [ ] Anwendungsfehler werden mit `isError: true` in `tool-result` zurückgegeben (nicht als JSON-RPC-Error)
- [ ] **Input- und Schema-Validierungsfehler laufen über den Execution-Pfad**, nicht über JSON-RPC (SEP-1303) — gilt auf beiden Baselines
- [ ] Die Fehlermeldung eines Validierungsfehlers nennt das betroffene Feld und den erwarteten Wertebereich; ohne das ist der nächste Versuch geraten
- [ ] Standardisierte Fehlercodes für Protocol-Level-Errors
- [ ] Auf `mcp_spec_version: 2026-07-28`: keine eigenen Codes im reservierten Bereich `-32020`…`-32099`; «resource not found» ist `-32602`, nicht `-32002`
- [ ] Mindestens 1 dokumentierter Test deckt Execution-Error-Pfad ab
- [ ] Mindestens 1 dokumentierter Test deckt Protocol-Error-Pfad ab (falsches Tool)
- [ ] Mindestens 1 Test belegt, dass ein **ungültiges Argument** als Execution-Error zurückkommt und nicht als JSON-RPC-Error

### Evidence

- src/discover_swiss_mcp/server.py:200-222 — _fail() logs the original, re-raises a masked ToolError; SDK turns ToolError into CallToolResult isError=true
- src/discover_swiss_mcp/server.py:236-242 — every tool body wrapped in try/except Exception -> _fail (same pattern at 251-257, 266-272, 281-287, 296-302, 311-317, 326-332, 341-349)
- src/discover_swiss_mcp/tools.py:697-705,708-716 — operational states (quota_exhausted, upstream_unreachable, search_unavailable) returned as structured result with degraded+hint, never as JSON-RPC error
- src/discover_swiss_mcp/tools.py:387, 275, 1641-1643 — input validators raise ValueError naming the field; arrive as execution errors
- runtime (in-memory Client, mcp 2.2.0): search params.page=-5 -> is_error=True, text names 'params.page' and 'greater than or equal to 1'; find_accommodation without near/locality -> is_error=True, 'Give `near` or `locality`'
- runtime (real stdio, python -m discover_swiss_mcp): tools/call no_such_tool -> result isError=true 'Unknown tool: no_such_tool', NOT a JSON-RPC error object
- tests/test_server.py:179-188 — missing key: execution-error path tested (is_error True, message names DISCOVER_SWISS_KEY)
- tests/test_server.py:191-196 — invalid argument returns is_error True and makes no upstream call
- grep -rnE '-320[2-9][0-9]|-3200[0-9]|-3201[0-9]|-32002' src/ -> no hit (exit 1); control 'code=-32021' matches -> no custom codes in the reserved range

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:200-222 — _fail() logs the original, re-raises a masked ToolError; SDK turns ToolError into CallToolResult isError=true
- src/discover_swiss_mcp/server.py:236-242 — every tool body wrapped in try/except Exception -> _fail (same pattern at 251-257, 266-272, 281-287, 296-302, 311-317, 326-332, 341-349)
- src/discover_swiss_mcp/tools.py:697-705,708-716 — operational states (quota_exhausted, upstream_unreachable, search_unavailable) returned as structured result with degraded+hint, never as JSON-RPC error
- src/discover_swiss_mcp/tools.py:387, 275, 1641-1643 — input validators raise ValueError naming the field; arrive as execution errors
- runtime (in-memory Client, mcp 2.2.0): search params.page=-5 -> is_error=True, text names 'params.page' and 'greater than or equal to 1'; find_accommodation without near/locality -> is_error=True, 'Give `near` or `locality`'
- runtime (real stdio, python -m discover_swiss_mcp): tools/call no_such_tool -> result isError=true 'Unknown tool: no_such_tool', NOT a JSON-RPC error object
- tests/test_server.py:179-188 — missing key: execution-error path tested (is_error True, message names DISCOVER_SWISS_KEY)
- tests/test_server.py:191-196 — invalid argument returns is_error True and makes no upstream call
- grep -rnE '-320[2-9][0-9]|-3200[0-9]|-3201[0-9]|-32002' src/ -> no hit (exit 1); control 'code=-32021' matches -> no custom codes in the reserved range

**Geschlossen**
- 7 of 9 criteria met. Classification of execution vs validation errors is correct and tested (SEP-1303 satisfied). The protocol-error side is missing: unknown tool comes back as isError result (SDK default) and no test pins the protocol-error path.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die MCP-Spezifikation fordert eine strikte Trennung zwischen zwei Fehler-Typen. Werden sie verwechselt, kann das LLM den Fehler nicht korrekt interpretieren und bricht in eine Halluzinations- oder Sackgassen-Schleife.

### Remediation

Add a test that calls an unknown tool and asserts the observed contract; if the target is spec conformance, map unknown-tool to a JSON-RPC -32601 (e.g. raise MCPError in a call_tool override) or document the SDK behaviour as accepted. Optionally set isError=true alongside degraded for upstream_unreachable/quota states.

**Disposition:** An unknown tool is answered as isError result instead of JSON-RPC -32601; this is mcp 2.2.0 MCPServer default behaviour, not server code. Revisit at the next SDK minor.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-001` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
