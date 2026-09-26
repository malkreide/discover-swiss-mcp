## Finding: OBS-007 — Fehler-Details bleiben nach innen diagnostizierbar

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-007` |
| **PDF-Reference** | Custom (Portfolio-Fundstück swiss-efv-mcp#16) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Messages after exhausted retries do not state the number of attempts (client.py:737, 743, 796, 800)
- Unreachable/5xx messages name the service ('discover.swiss') but not the endpoint path; path is only in the per-retry log events
- No test pins the message for str(exc)=='' — tests/test_client.py:258-269 use ConnectError('no route')/ReadTimeout('slow') and only assert 'discover.swiss' in the message

### Expected Behavior

- [ ] Meldungen, die der Server für sich behält (Log **und** intern geworfene Exceptions), nennen den **Exception-Typ**, nicht nur `str(exc)`
- [ ] Bei leerem `str(exc)` bleibt ein vollständiger Satz stehen — ein Fallback wie `or "no further detail"` oder ein Format, das ohne die Message auskommt
- [ ] Das **Ziel** ist benannt (Host, Endpoint, Datensatz-Key) — ohne Query-String, Header oder Credentials
- [ ] Nach erschöpften Retries steht die **Anzahl Versuche** in der Meldung — «nach Retries» allein sagt nicht, ob zwei oder zwanzig
- [ ] `raise ... from exc` verkettet die Ursache, damit der ursprüngliche Traceback nicht verloren geht
- [ ] Richtung nach aussen bleibt maskiert: Der Detailtext taucht **nicht** im Tool-Result auf (`OBS-002` gilt unverändert)
- [ ] Mindestens ein Test prüft den Meldungsinhalt für den Fall `str(exc) == ""` — ohne ihn verfällt der Text beim nächsten Refactoring unbemerkt

### Evidence

- src/discover_swiss_mcp/client.py:735-743 — network failure after retries: UpstreamUnavailableError(f'discover.swiss is not reachable ({type(exc).__name__}).') from exc — type named, cause chained, no str(exc)
- src/discover_swiss_mcp/client.py:725-728 — total-budget timeout message names the budget, chained from exc
- src/discover_swiss_mcp/client.py:745, 801 — retry log events carry path, reason=type(exc).__name__ / status, delay
- runtime (respx, side_effect ConnectTimeout(''), ReadTimeout(''), ConnectError('')): messages 'discover.swiss is not reachable (ConnectTimeout).' etc., __cause__ is the original type; 5xx exhaustion -> 'discover.swiss answered HTTP 503.'
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — outward direction masked: the model sees fixed DEGRADED_HINTS, not the exception text

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:735-743 — network failure after retries: UpstreamUnavailableError(f'discover.swiss is not reachable ({type(exc).__name__}).') from exc — type named, cause chained, no str(exc)
- src/discover_swiss_mcp/client.py:725-728 — total-budget timeout message names the budget, chained from exc
- src/discover_swiss_mcp/client.py:745, 801 — retry log events carry path, reason=type(exc).__name__ / status, delay
- runtime (respx, side_effect ConnectTimeout(''), ReadTimeout(''), ConnectError('')): messages 'discover.swiss is not reachable (ConnectTimeout).' etc., __cause__ is the original type; 5xx exhaustion -> 'discover.swiss answered HTTP 503.'
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — outward direction masked: the model sees fixed DEGRADED_HINTS, not the exception text

**Geschlossen**
- 5 of 7 criteria met. The dangerous pattern (f'...: {exc}') is absent; type and cause survive empty httpx messages (verified at runtime). Missing: attempt count, endpoint in final message, and a test holding the text.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Genau das ist der Fall, sobald eine Exception in eine eigene Meldung interpoliert wird:

### Remediation

Include attempts and path in the final message, e.g. f'discover.swiss not reachable after {retry_index+1} attempts: {type(exc).__name__} (path={path})', and add a respx test with httpx.ConnectTimeout('') asserting type name, path, attempt count and __cause__.

**Disposition:** Name the attempt count and the endpoint path in the final error after exhausted retries.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
