## Finding: OBS-003 — Structured Logging mit RFC 5424 Severity-Stufen

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-003` |
| **PDF-Reference** | Sec 6.3 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Only three distinct severities in use (info, warning, error/exception); debug is never emitted — criterion 'at least 4 levels (debug, info, warning, error)' not met
- Bound context has tool + correlation_id but no session_id / client identity

### Expected Behavior

- [ ] Structured Logger (structlog/pino/loguru) im `dependencies`
- [ ] JSON oder logfmt als Output-Format
- [ ] Mindestens 4 Severity-Stufen aktiv genutzt (debug, info, warning, error)
- [ ] Pro Tool-Call: bound context (tool name, session_id, correlation_id)
- [ ] Keine `print()`-Statements im Tool-Code (siehe OBS-004 für stdio)

### Evidence

- pyproject.toml:37 — structlog>=24.1.0,<27 in [project].dependencies
- src/discover_swiss_mcp/logging_config.py:68-82 — structlog JSONRenderer, add_log_level, ISO timestamp
- src/discover_swiss_mcp/logging_config.py:93-95 — tool_logger binds tool name and a fresh correlation_id per call; used at server.py:236,251,266,281,296,311,326,341
- grep of logger/log calls in src/: info (12), warning (6), error (4), exception (1); no debug
- grep -rnE '\bprint\(|sys\.stdout' src/ -> no hit (exit 1); control 'print("hi")' matches
- runtime: stderr lines are single JSON objects with event/level/timestamp fields (server start)

### Gemessen / Geschlossen / Offen

**Gemessen**
- pyproject.toml:37 — structlog>=24.1.0,<27 in [project].dependencies
- src/discover_swiss_mcp/logging_config.py:68-82 — structlog JSONRenderer, add_log_level, ISO timestamp
- src/discover_swiss_mcp/logging_config.py:93-95 — tool_logger binds tool name and a fresh correlation_id per call; used at server.py:236,251,266,281,296,311,326,341
- grep of logger/log calls in src/: info (12), warning (6), error (4), exception (1); no debug
- grep -rnE '\bprint\(|sys\.stdout' src/ -> no hit (exit 1); control 'print("hi")' matches
- runtime: stderr lines are single JSON objects with event/level/timestamp fields (server start)

**Geschlossen**
- 3 of 5 criteria fully met (structured logger dep, JSON output, no print); level coverage and session binding short.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: MCP-Server-Logs müssen strukturiert sein (JSON oder logfmt), nicht plaintext. Das ermöglicht Aggregation in Datadog/Splunk/Loki ohne Regex-Parsing, korrelierte Suche über Correlation-IDs, und konsistente Severity-Filterung.

### Remediation

Add debug-level events at useful points (cache hit/miss, request params after sanitisation) and bind the MCP session/request id from ctx in tool_logger.

**Disposition:** Emit debug events on the request path (cache hit/miss, fallback step).

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
