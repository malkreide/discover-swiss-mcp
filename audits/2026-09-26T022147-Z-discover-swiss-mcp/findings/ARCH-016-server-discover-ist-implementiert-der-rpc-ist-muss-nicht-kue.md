## Finding: ARCH-016 — server/discover ist implementiert — der RPC ist MUSS, nicht Kür

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-016` |
| **PDF-Reference** | SEP-2575 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Identity version is empty: MCPServer(...) at server.py:147-161 passes no version=; SDK default version '' (.venv/.../mcp/server/mcpserver/server.py:166) — package metadata version 0.1.0 is not used
- No test calls server/discover and checks versions, capabilities and identity separately (grep tests/ → 0); no Gegenprobe
- Capabilities advertise resources.subscribe/prompts although none exist (SDK default)
- Whether mcp 2.0.0 (the pinned lower bound) already ships server/discover and cache_hints was not verifiable offline

### Expected Behavior

- [ ] `server/discover` antwortet, über **jeden** bedienten Transportpfad (`ARCH-013`)
- [ ] Die Antwort nennt die unterstützten Protokollversionen als Liste, nicht als einzelnen String
- [ ] Die Antwort nennt die Server-Capabilities, inklusive `extensions` sofern welche geführt werden (`ARCH-021`)
- [ ] Die Antwort nennt die Server-Identität (Name, Version) — und die Version stammt aus den Paket-Metadaten, nicht aus einem Literal (`IDENT-002`)
- [ ] Stammt der RPC aus dem SDK, ist dessen Mindestversion im Manifest gepinnt
- [ ] Ein Test ruft `server/discover` auf und prüft alle drei Bestandteile einzeln — nicht nur, dass ein 200 zurückkam
- [ ] **Gegenprobe:** Der Test ist einmal gegen einen Server ohne den Handler gelaufen und hat dort angeschlagen

### Evidence

- src/discover_swiss_mcp/server.py:84 — CACHE_HINTS includes 'server/discover'; handler supplied by SDK (.venv/.../mcp/server/lowlevel/server.py:449,661-675), mcp 2.2.0 installed, pyproject.toml:34 mcp>=2,<3
- runtime HTTP: server/discover → supportedVersions ['2026-07-28'], capabilities {prompts, resources, tools}, instructions, resultType complete, ttlMs 300000, cacheScope public
- runtime stdio: same server/discover response via python -m discover_swiss_mcp
- runtime: _meta io.modelcontextprotocol/serverInfo = {name: 'discover_swiss_mcp', version: ''}

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:84 — CACHE_HINTS includes 'server/discover'; handler supplied by SDK (.venv/.../mcp/server/lowlevel/server.py:449,661-675), mcp 2.2.0 installed, pyproject.toml:34 mcp>=2,<3
- runtime HTTP: server/discover → supportedVersions ['2026-07-28'], capabilities {prompts, resources, tools}, instructions, resultType complete, ttlMs 300000, cacheScope public
- runtime stdio: same server/discover response via python -m discover_swiss_mcp
- runtime: _meta io.modelcontextprotocol/serverInfo = {name: 'discover_swiss_mcp', version: ''}

**Geschlossen**
- RPC answers on both transports with a version list and capabilities; identity version is blank and no test holds the three parts.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Wenn der `initialize`-Handshake wegfällt (`ARCH-015`), fehlt der Ort, an dem ein Server bisher gesagt hat, wer er ist und was er kann. `server/discover` ist dieser Ort — und die Spec ist an dieser Stelle asymmetrisch formuliert:

### Remediation

Pass version=__version__ (from package metadata) to MCPServer; add a test via mcp.Client asserting supportedVersions == ['2026-07-28'], 'tools' in capabilities, serverInfo.version == importlib.metadata.version('discover-swiss-mcp'); raise the lower bound to the first mcp 2.x that has cache_hints.

**Disposition:** serverInfo.version is empty: pass version=__version__ to MCPServer and test it on the wire.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-016` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
