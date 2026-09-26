## Finding: SEC-013 — API-Key-Storage: Secret Manager statt Plain-Text Env-Vars

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-013` |
| **PDF-Reference** | Sec 4 (Empirie 2025) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No secret-access audit (criterion 6): no secret manager and no log event for key use
- Stufe-1 choice is documented in SECURITY.md but without the explicit justification the check asks for (data class Public Open Data, BYOK, local deployment) and not in a secret-management document
- No reload mechanism without restart (TTL cache/reload); rotation requires a process restart — acceptable for local stdio but not what criterion 5 names

### Expected Behavior

- [ ] Bei `Verwaltungsdaten`/`PII`: Stufe 3 (Secret Manager) oder 4 (Workload Identity)
- [ ] Bei `Public Open Data`: Stufe 1 ist akzeptabel, aber dokumentiert in `docs/secret-management.md`
- [ ] Container-Image enthält keine Secrets im Layer (`docker history`-Test bestanden)
- [ ] Secret-Manager-Region ist Schweiz/EU (DSG, siehe CH-001)
- [ ] Rotation ist möglich ohne Code-Änderung (TTL-Cache oder Reload-Mechanismus)
- [ ] Secret-Access wird auditiert (Secret-Manager-eigenes Audit-Log oder OBS-005)

### Evidence

- src/discover_swiss_mcp/config.py:45 — api_key held as pydantic SecretStr; config.py:59-61 — auth_header is the only unwrap; config.py:75 — safe_summary logs only 'set'/'missing'
- src/discover_swiss_mcp/config.py:91 — key read from env var DISCOVER_SWISS_KEY only (Stufe 1, plain env var); no file-based config
- tests/test_smoke.py:60-68 — asserts key absent from repr/str/model_dump_json/repr(client) and present only in the outbound header
- SECURITY.md:12-25 — documents env-only storage, SecretStr masking, .gitignore coverage and 'rotate first' if pushed
- .gitignore — ignores .env, .env.*, *.key, *.pem, credentials.json, secrets.yaml, config.local.*
- src/discover_swiss_mcp/server.py:117-118 — settings loaded once per process in the lifespan; rotation = change env + restart, no code change

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:45 — api_key held as pydantic SecretStr; config.py:59-61 — auth_header is the only unwrap; config.py:75 — safe_summary logs only 'set'/'missing'
- src/discover_swiss_mcp/config.py:91 — key read from env var DISCOVER_SWISS_KEY only (Stufe 1, plain env var); no file-based config
- tests/test_smoke.py:60-68 — asserts key absent from repr/str/model_dump_json/repr(client) and present only in the outbound header
- SECURITY.md:12-25 — documents env-only storage, SecretStr masking, .gitignore coverage and 'rotate first' if pushed
- .gitignore — ignores .env, .env.*, *.key, *.pem, credentials.json, secrets.yaml, config.local.*
- src/discover_swiss_mcp/server.py:117-118 — settings loaded once per process in the lifespan; rotation = change env + restart, no code change

**Geschlossen**
- Data class is Public Open Data and deployment is local-only, so plain env var (Stufe 1) is acceptable provided it is documented. Key handling in code is exemplary (SecretStr, single unwrap, test). Container and region criteria are not applicable (no image, no secret manager). Audit trail is absent and the Stufe-1 rationale is implicit → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: ARCH-005 verlangt: **keine Hardcoded Secrets im Code**. SEC-013 geht weiter: in Production reichen Plain-Text Env-Vars nicht aus. Empirisch werden 53% der OSS-MCP-Server mit langlebigen Static API Keys betrieben — die in `.env`-Dateien, Container-Images, CI-Logs, und Container-Filesystem-Dumps geleakt werden.

### Remediation

Add a short 'Secret management' section (README or docs/secret-management.md) stating Stufe 1 is used deliberately because the key is a personal BYOK key for public open data on a local process, how to rotate (portal → env → restart), and that a secret manager is required if the server is ever deployed shared/cloud.

**Disposition:** Key in an environment variable, held as SecretStr, never logged (tested). No secret manager for a local bring-your-own-key tool; the reason goes into SECURITY.md.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-013` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
