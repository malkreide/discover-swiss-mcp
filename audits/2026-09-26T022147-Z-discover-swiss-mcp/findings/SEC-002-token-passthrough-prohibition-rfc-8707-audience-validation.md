## Finding: SEC-002 — Token Passthrough Prohibition (RFC 8707 Audience Validation)

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-002` |
| **PDF-Reference** | Sec 4.2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No inbound token verification exists at all, so the aud/iss/RFC 8707 criteria (1, 2, 5, 6) are not implemented — the HTTP transport is unauthenticated
- Consequence of the above: any caller that can reach the HTTP port spends the operator's BYOK subscription key (runtime probe: unauthenticated call → upstream request with operator key). Mitigated by the loopback default bind, not by a control
- No user identity propagation (criterion 4) — single-user server, no identity to propagate

### Expected Behavior

- [ ] Token-Verifizierung prüft `aud`-Claim gegen erwarteten Wert
- [ ] Falsche/fehlende Audience → HTTP 401 (nicht 200 mit weiterem Versuch)
- [ ] Upstream-Calls verwenden eigenes Service-Account-Token, nicht Client-Token
- [ ] User-Identität wird via separatem Header (`X-Acting-On-Behalf-Of` o.ä.) propagiert für Audit-Trail
- [ ] `iss`-Claim des **Tokens** wird ebenfalls validiert (Token-Provenienz)
- [ ] Der erwartete `iss` stammt aus einer serverseitig aufgezeichneten Zuordnung, nicht aus dem Token selbst — ein Token, das seinen eigenen Issuer bestimmt, validiert sich selbst
- [ ] Bei `auth_model == "OAuth-Proxy"`: Der `iss`-**Parameter der Authorization-Response** wird nach RFC 9207 geprüft, bevor der Code eingelöst wird — das ist eine andere Prüfung an einer anderen Stelle und steht in `SEC-025`

### Evidence

- src/discover_swiss_mcp/client.py:652-666 — request_headers() builds every upstream header from settings only (Ocp-Apim-Subscription-Key via settings.auth_header, User-Agent, Accept, Accept-Language from the Literal-validated `lang`, categoryVersion); no inbound value is copied
- src/discover_swiss_mcp/config.py:59-61 — auth_header is the single place the server-owned BYOK key is unwrapped; the key comes from DISCOVER_SWISS_KEY (config.py:91), not from any client request
- src/ — grep 'request\.headers|Authorization|headers\.get\(|ctx\.request_context\.request' finds no read of inbound request headers (only net.py:146 reads the upstream response Location header); pattern verified to fire on a control line
- runtime (audit probe, in-process uvicorn on 127.0.0.1:18780 with net.safe_request patched to capture outbound headers): tools/call source_status sent with 'Authorization: Bearer ATTACKER-TOKEN', 'Cookie', 'Mcp-Param-Evil' → HTTP 200; 3 upstream calls captured, header names [accept, accept-language, categoryversion, ocp-apim-subscription-key, user-agent], authorization/cookie absent, ATTACKER nowhere, subscription key == operator key (positive control: the capture does see the real key header)
- runtime: /.well-known/oauth-protected-resource → 404; no inbound auth layer exists on the streamable-http transport

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:652-666 — request_headers() builds every upstream header from settings only (Ocp-Apim-Subscription-Key via settings.auth_header, User-Agent, Accept, Accept-Language from the Literal-validated `lang`, categoryVersion); no inbound value is copied
- src/discover_swiss_mcp/config.py:59-61 — auth_header is the single place the server-owned BYOK key is unwrapped; the key comes from DISCOVER_SWISS_KEY (config.py:91), not from any client request
- src/ — grep 'request\.headers|Authorization|headers\.get\(|ctx\.request_context\.request' finds no read of inbound request headers (only net.py:146 reads the upstream response Location header); pattern verified to fire on a control line
- runtime (audit probe, in-process uvicorn on 127.0.0.1:18780 with net.safe_request patched to capture outbound headers): tools/call source_status sent with 'Authorization: Bearer ATTACKER-TOKEN', 'Cookie', 'Mcp-Param-Evil' → HTTP 200; 3 upstream calls captured, header names [accept, accept-language, categoryversion, ocp-apim-subscription-key, user-agent], authorization/cookie absent, ATTACKER nowhere, subscription key == operator key (positive control: the capture does see the real key header)
- runtime: /.well-known/oauth-protected-resource → 404; no inbound auth layer exists on the streamable-http transport

**Geschlossen**
- The passthrough prohibition itself is satisfied with positive code and runtime evidence: client tokens never reach discover.swiss; upstream uses the server's own key. The audience/issuer criteria are unmet because the server accepts no inbound token at all. Counted as partial rather than pass because 4 of 7 criteria (aud check, 401 on wrong audience, iss validation, server-side issuer mapping) have no implementation; the practical exposure is bounded by the 127.0.0.1 default.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: «Token Passthrough» bezeichnet das unkritische Weiterreichen eines vom MCP-Client erhaltenen Access-Tokens an einen Upstream-Service (z.B. interne API, Drittanbieter-API). Auf den ersten Blick wirkt das pragmatisch — der Server muss kein eigenes Auth-Konzept implementieren —, ist aber ein Verstoss gegen die OAuth-2.0-Sicherheitsarchitektur.

### Remediation

Document in README/SECURITY.md that the HTTP transport has no inbound authentication and must stay on loopback; if it is ever exposed beyond loopback, add inbound bearer auth (TokenVerifier with aud/iss validation against server-side configured values, 401 on mismatch) before serving tools, and keep the upstream key server-owned as today.

**Disposition:** The HTTP transport has no inbound authentication; client tokens are never forwarded upstream (verified). The server is local-only by design (loopback default). Catalogue question recorded in the audit: auth_model 'API-Key' here means a bring-your-own upstream key, not inbound auth. Accepted together with the SEC-016 fix that refuses a non-loopback bind without explicit opt-in.

### Effort Estimate

M

### Dependencies / Blockers

Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).

### Verification After Fix

- Re-Audit von `SEC-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
