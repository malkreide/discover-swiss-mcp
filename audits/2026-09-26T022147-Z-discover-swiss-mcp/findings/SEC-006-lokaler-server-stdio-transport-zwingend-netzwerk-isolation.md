## Finding: SEC-006 — Lokaler Server: stdio-Transport zwingend (Netzwerk-Isolation)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-006` |
| **PDF-Reference** | Sec 4.5 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README has no Claude Desktop / mcpServers configuration example for the local stdio use-case (criterion 3 only partly met)
- README has no separate cloud-deployment section with security notes (criterion 4 unmet); the only network note is SECURITY.md:39-41, which references a host allow-list the code does not provide (see SEC-024)

### Expected Behavior

- [ ] Default-Transport (ohne ENV-Var) ist `stdio`
- [ ] SSE/HTTP-Transport nur via expliziter `MCP_TRANSPORT`-ENV-Var aktivierbar
- [ ] README dokumentiert lokalen Use-Case primär (stdio + Claude Desktop)
- [ ] README dokumentiert Cloud-Use-Case separat mit Sicherheitshinweisen
- [ ] Default-Start öffnet keinen TCP-Port (Runtime-Test)

### Evidence

- src/discover_swiss_mcp/config.py:48 — Settings.transport default 'stdio'; config.py:105-106 — DISCOVER_SWISS_MCP_TRANSPORT defaults to 'stdio', anything other than stdio/streamable-http is a ConfigError
- src/discover_swiss_mcp/server.py:358-370 — HTTP (uvicorn) only when settings.transport == 'streamable-http', else mcp.run() (stdio)
- runtime (audit): `python -m discover_swiss_mcp` without transport env → 0 listening TCP sockets for the PID (/proc/<pid>/fd × /proc/net/tcp state 0A); control: same check on a streamable-http run → 1 listening socket
- README.md:139-143 — stdio shown first ('stdio (Claude Desktop and other local clients)'), HTTP shown as explicit opt-in with 'binds to 127.0.0.1:8000 by default (localhost only)'
- README.md:111 — 'Dual transport — stdio (Claude Desktop) and Streamable HTTP (cloud)'

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:48 — Settings.transport default 'stdio'; config.py:105-106 — DISCOVER_SWISS_MCP_TRANSPORT defaults to 'stdio', anything other than stdio/streamable-http is a ConfigError
- src/discover_swiss_mcp/server.py:358-370 — HTTP (uvicorn) only when settings.transport == 'streamable-http', else mcp.run() (stdio)
- runtime (audit): `python -m discover_swiss_mcp` without transport env → 0 listening TCP sockets for the PID (/proc/<pid>/fd × /proc/net/tcp state 0A); control: same check on a streamable-http run → 1 listening socket
- README.md:139-143 — stdio shown first ('stdio (Claude Desktop and other local clients)'), HTTP shown as explicit opt-in with 'binds to 127.0.0.1:8000 by default (localhost only)'
- README.md:111 — 'Dual transport — stdio (Claude Desktop) and Streamable HTTP (cloud)'

**Geschlossen**
- Code-side criteria (stdio default, HTTP only via explicit env var, no port on default start — runtime verified with control) are met. The two documentation criteria are only partly met: local use is shown as a bare command, and HTTP is labelled '(cloud)' without any cloud section or security guidance.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Lokale MCP-Server laufen mit den Privilegien des Users — sie haben Zugriff auf das Filesystem, Netzwerk-Interfaces, Subprozess-Spawning, Environment-Variablen, gespeicherte SSH-Keys, Browser-Cookies. Ein lokaler Server, der gleichzeitig auf einem Netzwerk-Port lauscht, weitet diese User-Privilegien auf jede Entity aus, die diesen Port erreichen kann.

### Remediation

Add to README a 'Local use (Claude Desktop)' block with the full mcpServers JSON (command, args, env DISCOVER_SWISS_KEY) and a separate 'HTTP transport' section stating it is for loopback/local testing unless fronted by auth and a host allow-list, with the security caveats.

**Disposition:** README: Claude Desktop configuration example for stdio.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
