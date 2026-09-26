## Finding: SEC-028 — Egress-Guard: Policy-Verstoss und Auflösungsfehler sind unterscheidbar

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-028` |
| **PDF-Reference** | Custom (Katalog-Lücke, aufgefallen bei zh-education-mcp, 2026-08-03) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Policy violation and resolution failure are not distinguishable by a code-read discriminator; the empty-answer case shares EgressError with the policy case
- Transient resolver failures are never retried (gaierror bypasses the retry ladder; empty answer is re-raised as EgressError)
- User-facing message for an empty DNS answer names the egress policy — the exact misleading-message failure the check describes
- gaierror escapes status(): source_status, the diagnostic tool, fails instead of reporting reachable=false
- No tests for either the transient or the deterministic case with retry assertions

### Expected Behavior

- [ ] Policy-Verstoss und Auflösungsfehler verlassen den Guard als **verschiedene Exception-Typen** — oder als ein Typ mit einem Diskriminator, den der Code liest (Attribut, Enum), nicht als Text im Meldungsstring
- [ ] Die Retry-Politik entscheidet an diesem Diskriminator: Policy-Verstoss ohne Wiederholung, Auflösungsfehler mit
- [ ] Die nutzerseitige Meldung nennt im transienten Fall weder die Egress-Policy noch die Allow-List-Konfiguration als Ursache
- [ ] Kein Sammel-`except` und keine Fehlerabbildung, die die beiden Typen vor der Ausgabe wieder zusammenführt
- [ ] Beide Lagen sind getestet — der transiente Fall mit Wiederholung, der deterministische ohne; beide Tests fallen, wenn die Typen zusammengelegt werden

### Evidence

- src/discover_swiss_mcp/net.py:58-59 — a single EgressError(ValueError) type for all guard outcomes, no discriminator attribute
- src/discover_swiss_mcp/net.py:96-98 — an empty DNS answer raises EgressError('No DNS answer …') — the same type as a policy violation (net.py:100-103)
- src/discover_swiss_mcp/net.py:75-78 — loop.getaddrinfo is not wrapped: socket.gaierror escapes the guard untyped
- src/discover_swiss_mcp/client.py:729-730 — `except net.EgressError: raise` (never retried); client.py:731 retries only httpx.RequestError, which gaierror is not
- src/discover_swiss_mcp/server.py:218-219 — every EgressError is mapped to 'The outbound request was blocked by the server's egress policy.'
- src/discover_swiss_mcp/client.py:1103-1106 — status() catches DiscoverSwissError and EgressError only
- runtime (audit, socket.getaddrinfo raising gaierror EAI_AGAIN): client._call → socket.gaierror escapes, isEgressError False, isRequestError False, 1 attempt, 0 retries; client.status() raised gaierror (source_status would fail with 'unexpected internal error'); empty DNS answer → EgressError 'No DNS answer for …' which the tool layer reports as an egress-policy block

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:58-59 — a single EgressError(ValueError) type for all guard outcomes, no discriminator attribute
- src/discover_swiss_mcp/net.py:96-98 — an empty DNS answer raises EgressError('No DNS answer …') — the same type as a policy violation (net.py:100-103)
- src/discover_swiss_mcp/net.py:75-78 — loop.getaddrinfo is not wrapped: socket.gaierror escapes the guard untyped
- src/discover_swiss_mcp/client.py:729-730 — `except net.EgressError: raise` (never retried); client.py:731 retries only httpx.RequestError, which gaierror is not
- src/discover_swiss_mcp/server.py:218-219 — every EgressError is mapped to 'The outbound request was blocked by the server's egress policy.'
- src/discover_swiss_mcp/client.py:1103-1106 — status() catches DiscoverSwissError and EgressError only
- runtime (audit, socket.getaddrinfo raising gaierror EAI_AGAIN): client._call → socket.gaierror escapes, isEgressError False, isRequestError False, 1 attempt, 0 retries; client.status() raised gaierror (source_status would fail with 'unexpected internal error'); empty DNS answer → EgressError 'No DNS answer for …' which the tool layer reports as an egress-policy block

**Geschlossen**
- The guard throws one type for a policy violation and for an empty resolution, and lets a real resolver error escape untyped and unretried. Runtime probes confirm all three behaviours. 0 of 5 criteria met.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Egress-Guard scheitert an zwei grundverschiedenen Lagen, und beide laufen durch dieselbe Funktion:

### Remediation

In net.py add EgressPolicyViolation(EgressError, retryable=False) and EgressResolutionError(EgressError, retryable=True); wrap getaddrinfo (gaierror, OSError, empty answer) into EgressResolutionError; in client._call retry EgressResolutionError on the existing ladder and re-raise policy violations; in server._fail map the two to distinct messages (resolution: 'temporarily not resolvable, retry; configuration unaffected'); catch EgressResolutionError in status(); add the two tests from the check and run the merge-types mutation once.

**Disposition:** Split EgressError into a policy block and a resolution failure; retry only the latter, and stop status() from crashing on socket.gaierror.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-028` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
