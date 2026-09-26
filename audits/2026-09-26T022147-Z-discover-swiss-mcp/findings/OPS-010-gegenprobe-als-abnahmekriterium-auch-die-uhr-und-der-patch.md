## Finding: OPS-010 — Gegenprobe als Abnahmekriterium — auch die Uhr und der Patch

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-010` |
| **PDF-Reference** | Custom (Katalog-Lücke gegen mcp-transport-hardening-skill Regel 6, 2026-08-07) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Surviving mutation M1: TOTAL_BUDGET = 25.0 -> 1e9 (client.py:248) — 215 passed. The wall-clock budget has no test at all, under fake or real time
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide (client_module.time is time); the event loop clock reads time.monotonic too
- No test guards the _sleep seam (no assertion that real asyncio.sleep still waits)
- No documentation of which test turns red per central assurance, no dated counter-test record, nothing in CONTRIBUTING.md (grep gegenprobe|mutation|negative control over tests/ and CONTRIBUTING.md -> no hit)

### Expected Behavior

- [ ] Für jede zentrale Zusicherung des Servers ist **dokumentiert**, welcher Test rot wird, wenn man sie bricht
- [ ] Die Gegenprobe ist **gefahren** worden, nicht nur vorgesehen — mit Datum oder Commit, an dem sie lief
- [ ] Mutationen, die **nicht** anschlagen, stehen im Befund; sie sind das Ergebnis, nicht der Ausschuss
- [ ] Jede Zusicherung über **Wanduhrzeit** hat mindestens einen Test unter **echter** Zeit; eine Uhr, die nur beim Schlafen vorrückt, ist dort kein Beleg
- [ ] Kein Test patcht ein **fremdes** Modul global (`modul.asyncio`, `modul.time`, `modul.random`); gepatcht wird eine eigene Naht (`modul._sleep`)
- [ ] Ein Test bewacht diese Naht — er zeigt, dass das echte `asyncio.sleep` nach der Fixture noch wirkt
- [ ] Der Weg, eine Gegenprobe zu fahren, steht im `CONTRIBUTING`; eine Praxis, die nur einer kennt, überlebt den nächsten Beitrag nicht
- [ ] **Gegenprobe zur Gegenprobe:** Es ist einmal gezeigt worden, dass die Mutations-Methode selbst anschlägt — eine Mutation, von der bekannt ist, dass sie einen Test bricht, bricht ihn auch

### Evidence

- src/discover_swiss_mcp/client.py:275-279 — own seam _sleep = asyncio.sleep; tests/conftest.py:75-84 patches client_module._sleep, not asyncio
- Mutation counter-tests run by the auditor on a scratch copy (PYTHONPATH pointed at the copy, verified via module __file__): M0 control RETRY_DELAYS (2,4,8)->(1,4,8): 1 failed (method fires); M2 egress allow-list disabled (net.py 'if False and host not in EGRESS_ALLOWLIST'): 1 failed; M3 POST redirect gate disabled: 1 failed; M4 key rendered in safe_summary: 1 failed
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide; re-read by the report author at bd0e371 (step 4 gate: third observation moved from gaps into evidence)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:275-279 — own seam _sleep = asyncio.sleep; tests/conftest.py:75-84 patches client_module._sleep, not asyncio
- Mutation counter-tests run by the auditor on a scratch copy (PYTHONPATH pointed at the copy, verified via module __file__): M0 control RETRY_DELAYS (2,4,8)->(1,4,8): 1 failed (method fires); M2 egress allow-list disabled (net.py 'if False and host not in EGRESS_ALLOWLIST'): 1 failed; M3 POST redirect gate disabled: 1 failed; M4 key rendered in safe_summary: 1 failed
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide; re-read by the report author at bd0e371 (step 4 gate: third observation moved from gaps into evidence)

**Geschlossen**
- 2 of 8 criteria met (counter-counter-test by the auditor; surviving mutation now on record). The suite does catch egress, redirect and secret regressions, but the wall-clock budget is unguarded and one test patches a foreign module globally.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Test, der grün bleibt, wenn man die Implementierung entfernt, prüft nichts. Er kostet Laufzeit, erzeugt eine Zeile im Report und eine Überzeugung, die durch nichts gedeckt ist — die teuerste Form von Testabdeckung, weil sie den Blick von der Stelle wegzieht, an der nichts steht.

### Remediation

Add a real-time test: respx side_effect sleeping 1 s with TOTAL_BUDGET monkeypatched to 0.05 on the client module, asserting UpstreamUnavailableError within <0.5 s; replace the time.monotonic patch with an own seam (_monotonic = time.monotonic in client.py); add a test that asyncio.sleep(0.05) still takes >=0.04 s under the sleeps fixture; document the counter-test procedure and results in CONTRIBUTING.md.

**Disposition:** Mutation TOTAL_BUDGET 25 -> 1e9 survives all 215 tests. Add a real-time budget test, replace the global time.monotonic patch with an own seam, guard the _sleep seam, document the counter-test procedure in CONTRIBUTING.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-010` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
