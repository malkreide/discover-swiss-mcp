## Finding: ARCH-014 — Retry-Politik gegenüber der Quelle: begrenzt, gestreut, gehorsam

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-014` |
| **PDF-Reference** | Custom (Katalog-Lücke, aufgefallen bei swiss-efv-mcp#16) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No jitter: client.py:236-241 deliberately deterministic (rationale: single-process client behind token bucket) — criterion unmet
- Retry-After only on 429 and only as integer seconds; 503 Retry-After ignored, HTTP-date form not parsed (client.py:546-548)
- Budget not bounded below the client timeout on all paths: a 429 extends the deadline by up to 30 s (client.py:772) → up to ~55 s; bucket.acquire() (client.py:714, 409-420, up to ~60 s) runs before asyncio.timeout and outside the deadline
- No test binds the wall-clock budget (no real-time slow-response test)

### Expected Behavior

Die ersten neun Kriterien setzen voraus, dass überhaupt wiederholt wird. Tut der Server das nicht, greift stattdessen der Abschnitt «Was gilt, wenn gar nicht wiederholt wird» — dann sind nur die drei dort genannten Bedingungen zu prüfen, und die letzten drei Kriterien dieser Liste.

- [ ] **Vorfrage:** Ob wiederholt wird, ist **festgestellt** — eigene Schleife, Bibliotheks-Dekorator **und** Transport-Ebene sind gelesen, nicht nur gegrept
- [ ] Wiederholt wird nur bei 5xx, 429, Timeout und Verbindungsfehler — **4xx ausser 429 bricht sofort ab**
- [ ] Der Backoff ist **gestreut** (Jitter), nicht rein deterministisch
- [ ] Wiederholt wird auch bei **Netzwerkfehlern und Timeouts**, nicht nur bei Status-Codes
- [ ] `Retry-After` bei 429/503 wird gelesen und **schlägt** die eigene Kurve, gedeckelt gegen unbrauchbar grosse Werte
- [ ] Der Deckel greift **nach** dem Jittern — nachgerechnet, nicht am Namen der Konstante abgelesen
- [ ] Es gibt ein **Gesamtbudget in Sekunden**, nicht nur eine Anzahl Versuche
- [ ] Das Budget hängt an einer **Wanduhr-Deadline**, nicht am Per-Operation-Timeout der HTTP-Bibliothek
- [ ] Das Budget liegt **unter dem Timeout des aufrufenden MCP-Clients** — sonst arbeitet der Server für niemanden
- [ ] Wiederholt wird auf **genau einer Ebene**; Transport-Retries der HTTP-Bibliothek stehen nachweislich auf null. **Das gilt auch für einen Server ohne eigene Schleife** — gesetzte Transport-Retries sind dort keine fehlende Politik, sondern eine ungeschriebene
- [ ] Schreibende Tools wiederholen nur mit Idempotency-Key (`ARCH-010`)
- [ ] Nach Erschöpfung: Fehler oder **gekennzeichnet** veralteter Cache — kein stilles Ausliefern alter Zahlen (`FID-003`)
- [ ] Die Werte sind im Test gebunden, nicht nur im Kommentar behauptet

### Evidence

- src/discover_swiss_mcp/client.py:707-807 — single retry loop in _call (hand-read); httpx.AsyncClient at :648 without transport= (retries 0); grep HTTPTransport|max_retries|Retry( src/ → 0 (negative control: hits .venv/.../httpx/_client.py:731)
- client.py:805-807 + tests/test_client.py:298-305 — other 4xx raise UpstreamRejectedError immediately, 1 call, no sleep
- client.py:731-747 + tests/test_client.py:258-262 — httpx.RequestError (network, timeouts) retried on the same ladder
- client.py:241 + tests/test_client.py:239-246 — fixed ladder 2/4/8 s, asserted exactly
- client.py:531-549,762-774 + tests/test_client.py:272-295 — 429 wait read from body ('Try again in N seconds') then Retry-After header, one retry, >30 s (RATE_LIMIT_MAX_WAIT :257) fails immediately
- client.py:248,703,716 — TOTAL_BUDGET 25 s as wall-clock deadline enforced with asyncio.timeout(remaining)
- client.py:776-781 — 403 quota is a state, never retried; exhaustion raises UpstreamUnavailableError mapped to degraded envelope (tools.py:697-705)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:707-807 — single retry loop in _call (hand-read); httpx.AsyncClient at :648 without transport= (retries 0); grep HTTPTransport|max_retries|Retry( src/ → 0 (negative control: hits .venv/.../httpx/_client.py:731)
- client.py:805-807 + tests/test_client.py:298-305 — other 4xx raise UpstreamRejectedError immediately, 1 call, no sleep
- client.py:731-747 + tests/test_client.py:258-262 — httpx.RequestError (network, timeouts) retried on the same ladder
- client.py:241 + tests/test_client.py:239-246 — fixed ladder 2/4/8 s, asserted exactly
- client.py:531-549,762-774 + tests/test_client.py:272-295 — 429 wait read from body ('Try again in N seconds') then Retry-After header, one retry, >30 s (RATE_LIMIT_MAX_WAIT :257) fails immediately
- client.py:248,703,716 — TOTAL_BUDGET 25 s as wall-clock deadline enforced with asyncio.timeout(remaining)
- client.py:776-781 — 403 quota is a state, never retried; exhaustion raises UpstreamUnavailableError mapped to degraded envelope (tools.py:697-705)

**Geschlossen**
- Retry exists and is well-scoped (what is retried, one layer, wall-clock deadline, 4xx abort). Jitter, full Retry-After handling and a hard total bound under the 30 s client timeout are missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Fast jeder Server im Portfolio wiederholt fehlgeschlagene Requests, und bis auf `OBS-007` («wie lautet die Meldung, wenn alle Versuche verbraucht sind») stellte der Katalog dazu keine Frage. Nicht *ob* wiederholt wird — das ist richtig —, sondern **was**, **wie schnell** und **wie lange**. Alle drei Antworten sind falsch, wenn niemand sie trifft: Die Voreinstellung ist «alles, sofort, unbegrenzt».

### Remediation

Add jitter after capping order (delay = min(base*2**n*(0.5+random()), MAX)); parse Retry-After on 503 and HTTP-date; move bucket.acquire inside the deadline or count it; cap deadline extension so total stays < 30 s; add a real-time test with a slow respx side effect and total_budget small.

**Disposition:** The 25 s budget can reach about 55 s after a 429 and rate-limiter waits are outside it; count both into the budget. Jitter stays off by design (single process behind a token bucket) and the reason is written next to RETRY_DELAYS.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-014` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
