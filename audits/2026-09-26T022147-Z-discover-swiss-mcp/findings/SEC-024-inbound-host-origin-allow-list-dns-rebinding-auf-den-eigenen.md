## Finding: SEC-024 — Inbound Host/Origin-Allow-List (DNS-Rebinding auf den eigenen Endpoint)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-024` |
| **PDF-Reference** | Sec 4.4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- TransportSecuritySettings is never wired; protection exists only as the SDK's loopback auto-default (criterion 1 unmet)
- No deployment-configured allow-list (no MCP_ALLOWED_HOSTS or equivalent) — a non-loopback bind cannot be protected at all
- Entries are not port-exact (wrong port accepted) — the SDK default uses ':*'
- Non-loopback bind without allow-list is silent (no startup warning) — protection is fail-open exactly as the check describes
- No tests for wrong-port rejection / allowed-port acceptance or for auth-not-rescuing-foreign-host
- SECURITY.md documents a control that does not exist

### Expected Behavior

- [ ] **Evidence 1:** `TransportSecuritySettings` ist im Code an den Transport verdrahtet, mit `enable_dns_rebinding_protection=True`
- [ ] Die Allow-List stammt aus der Deployment-Konfiguration (`MCP_ALLOWED_HOSTS`), nicht aus dem Code
- [ ] Einträge sind portgenau — ein Eintrag trägt seinen Port
- [ ] Loopback ist immer enthalten, mit dem tatsächlich bedienten Port
- [ ] Konfigurierte CORS-Origins sind in der Origin-Liste des Transports enthalten
- [ ] `*` wird aus der CORS-Konfiguration **nicht** übernommen
- [ ] Fehlt die Variable auf einem Nicht-Loopback-Bind, bleibt der Schutz aus **und eine Startwarnung sagt es**
- [ ] **Evidence 2:** Ein Test weist «richtiger Hostname, falscher Port» ab — nicht nur einen fremden Namen —, und derselbe Name auf dem **richtigen** Port wird bedient. Erst das Paar schliesst eine zurückgefallene Default-Policy aus
- [ ] Ein Test belegt, dass ein gültiges Auth-Token einen fremden Host nicht rettet
- [ ] Die Allow-List erreicht **jeden** Netzpfad, über den der Server bedient werden kann

### Evidence

- src/discover_swiss_mcp/server.py:364-368 — mcp.streamable_http_app(host=settings.host) with no transport_security argument; grep 'TransportSecuritySettings|transport_security|allowed_hosts|allowed_origins|ALLOWED_HOSTS|enable_dns_rebinding_protection' in src/ → no hit (control: 16 hits in the SDK's mcpserver/server.py)
- .venv/.../mcp/server/mcpserver/server.py:1155-1159 (mcp 2.2.0) — SDK auto-enables protection only for host in 127.0.0.1/localhost/::1, with wildcard-port entries '127.0.0.1:*', 'localhost:*', '[::1]:*'
- runtime (audit, loopback bind): Host: evil.example.com → 421; foreign Origin → 403; allowed Host 127.0.0.1:<port> → 200; but Host: 127.0.0.1:9999 (wrong port) → 200 — list is not port-exact
- runtime (audit, DISCOVER_SWISS_MCP_HOST=0.0.0.0): Host: evil.example.com → 200 and foreign Origin → 200; start log has no warning
- SECURITY.md:39-41 — claims 'A non-loopback bind needs an explicit host allow-list', but the code offers no variable or mechanism to configure one

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:364-368 — mcp.streamable_http_app(host=settings.host) with no transport_security argument; grep 'TransportSecuritySettings|transport_security|allowed_hosts|allowed_origins|ALLOWED_HOSTS|enable_dns_rebinding_protection' in src/ → no hit (control: 16 hits in the SDK's mcpserver/server.py)
- .venv/.../mcp/server/mcpserver/server.py:1155-1159 (mcp 2.2.0) — SDK auto-enables protection only for host in 127.0.0.1/localhost/::1, with wildcard-port entries '127.0.0.1:*', 'localhost:*', '[::1]:*'
- runtime (audit, loopback bind): Host: evil.example.com → 421; foreign Origin → 403; allowed Host 127.0.0.1:<port> → 200; but Host: 127.0.0.1:9999 (wrong port) → 200 — list is not port-exact
- runtime (audit, DISCOVER_SWISS_MCP_HOST=0.0.0.0): Host: evil.example.com → 200 and foreign Origin → 200; start log has no warning
- SECURITY.md:39-41 — claims 'A non-loopback bind needs an explicit host allow-list', but the code offers no variable or mechanism to configure one

**Geschlossen**
- Only the loopback auto-protection of the SDK is present (foreign Host 421, foreign Origin 403 on 127.0.0.1). The explicit wiring, env-sourced port-exact list, warning and tests are all absent, and a 0.0.0.0 bind accepts any Host/Origin (runtime). Fewer than half the criteria met → fail.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Angriff ist DNS-Rebinding, aber die **eingehende** Variante: Eine Seite im Netz des Betreibers löst ihren eigenen Hostnamen auf die Adresse dieses MCP-Servers auf und spricht dann aus dem Browser mit ihm. Der Angreifer braucht keinen Netzzugang — er braucht nur, dass jemand im richtigen Netz seine Seite öffnet. Was er erbt, ist alles, was der Server kann: Tool-Inventar, Filesystem-Zugriffe, hinterlegte Credentials.

### Remediation

Add build_transport_security(host, port) reading DISCOVER_SWISS_MCP_ALLOWED_HOSTS / _ALLOWED_ORIGINS (port-exact, loopback entries with the served port always included, '*' dropped), pass transport_security= to streamable_http_app, log a WARNING when the bind is non-loopback and the variable is empty; add tests: allowed host:port → 200, same name wrong port → 421, foreign host → 421, and a mutation check (remove transport_security → wrong-port test fails). Align SECURITY.md with the implementation.

**Disposition:** Wire TransportSecuritySettings with a port-exact host and origin allow-list; SECURITY.md currently describes an allow-list the code does not have.

### Effort Estimate

S

### Dependencies / Blockers

Zusammen mit SEC-016 umsetzen (derselbe Startpfad).

### Verification After Fix

- Re-Audit von `SEC-024` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
