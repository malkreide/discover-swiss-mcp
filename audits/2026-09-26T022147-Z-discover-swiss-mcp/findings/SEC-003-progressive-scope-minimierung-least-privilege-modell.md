## Finding: SEC-003 — Progressive Scope-Minimierung: Least-Privilege-Modell

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-003` |
| **PDF-Reference** | Sec 4.3 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No scope hierarchy defined and no per-tool scope requirements
- No per-call scope validation and no 403 + WWW-Authenticate insufficient_scope challenge
- No RFC 9728 Protected Resource Metadata (/.well-known/oauth-protected-resource → 404)
- Only the Origin→403 criterion is met (and only on loopback bind, via SDK default)

### Expected Behavior

- [ ] Scope-Hierarchie ist definiert (kein Omnibus `*:*`)
- [ ] Pro Tool dokumentierte erforderliche Scopes
- [ ] Server validiert Scopes pro Tool-Call (nicht nur beim Login)
- [ ] Bei Insufficient-Scope: HTTP 403 mit `WWW-Authenticate`-Header und konkretem Scope
- [ ] `/.well-known/oauth-protected-resource` wird bedient und nennt Ressourcen-Kennung, Autorisierungsserver und Scopes (RFC 9728, SEP-985)
- [ ] Die dort genannten `scopes_supported` decken sich mit der implementierten Scope-Hierarchie
- [ ] Bei ungültigem Origin antwortet der Transport `403`, nicht `400` (Spec 2025-11-25, Minor #3) — siehe `SEC-024`
- [ ] Initial-Login-Scope ist minimal (Discovery + Public-Read)
- [ ] Granularität: lese/schreibe + Datenklasse als separate Dimensionen
- [ ] Admin-Scopes sind explizit, nicht in Standard-Hierarchie eingebettet

### Evidence

- src/ — grep 'audience|aud|WWW-Authenticate|insufficient_scope|scope|oauth|jwt|Bearer|TokenVerifier|AuthSettings' finds only unrelated uses of the word 'scope' (tools.py:491 geographic scope, server.py:83-84 CacheHint scope='public'); no scope model, no per-tool scope check
- runtime: GET /.well-known/oauth-protected-resource and /.well-known/oauth-protected-resource/mcp → 404 (control: GET /mcp on same server → 405, server was up)
- runtime: POST /mcp with foreign Origin on loopback bind → HTTP 403 'Invalid Origin header' (criterion 7 met via SDK default)
- src/discover_swiss_mcp/server.py:170-175 — all 8 tools annotated readOnlyHint=True, destructiveHint=False (single read-only capability class)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/ — grep 'audience|aud|WWW-Authenticate|insufficient_scope|scope|oauth|jwt|Bearer|TokenVerifier|AuthSettings' finds only unrelated uses of the word 'scope' (tools.py:491 geographic scope, server.py:83-84 CacheHint scope='public'); no scope model, no per-tool scope check
- runtime: GET /.well-known/oauth-protected-resource and /.well-known/oauth-protected-resource/mcp → 404 (control: GET /mcp on same server → 405, server was up)
- runtime: POST /mcp with foreign Origin on loopback bind → HTTP 403 'Invalid Origin header' (criterion 7 met via SDK default)
- src/discover_swiss_mcp/server.py:170-175 — all 8 tools annotated readOnlyHint=True, destructiveHint=False (single read-only capability class)

**Geschlossen**
- auth_model is API-Key (BYOK upstream key) and the HTTP transport has no inbound OAuth at all, so none of the scope criteria is implemented. Measured strictly against the pass criteria this is a fail (1 of ~10 met). Practical risk is low: all tools are read-only over public open data and the transport binds loopback by default; the catalogue's applies_when (auth_model != none) maps a BYOK upstream key onto an inbound-OAuth check — worth a catalogue/profile review.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: OAuth-Scope-Design hat zwei Failure-Modes:

### Remediation

Either (a) record in README/SECURITY.md that the server has no inbound authorization and therefore a single implicit read-only scope, and keep HTTP loopback-only; or (b) if the HTTP transport is to be exposed, add OAuth resource-server support with a minimal read scope (e.g. data:read:public), per-tool scope checks returning 403 + WWW-Authenticate, and /.well-known/oauth-protected-resource.

**Disposition:** No OAuth scopes: there is no inbound OAuth. Same reasoning and same condition as SEC-002.

### Effort Estimate

L

### Dependencies / Blockers

Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).

### Verification After Fix

- Re-Audit von `SEC-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
