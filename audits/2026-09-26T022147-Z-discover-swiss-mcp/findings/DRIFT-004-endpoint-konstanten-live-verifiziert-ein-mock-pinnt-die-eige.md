## Finding: DRIFT-004 — Endpoint-Konstanten live verifiziert — ein Mock pinnt die eigene Annahme

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-004` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#35, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- List endpoints (the whole fallback path) and /status are not covered by any live test; /places, /foodEstablishments, /localbusinesses have never been called with the current select
- The live tests that exist have never been executed
- Live tests do not explicitly separate 404 (endpoint gone) from 5xx (transient)
- scripts/p3_stopgate_run.py and probes/probe_open.py are one-shot scripts, not a probe manifest run on a schedule

### Expected Behavior

- [ ] Jede Endpoint-Konstante wird von mindestens einem Live-Test oder einem Probe-Manifest abgedeckt
- [ ] Mocks registrieren gegen die importierte Konstante, nicht gegen ein wiederholtes URL-Literal
- [ ] Der Live-Test unterscheidet 404 (Endpoint weg) von 5xx (transient) — nur Ersteres ist ein Befund
- [ ] Die Abdeckung ist vollständig: kein Endpoint, der nur in Mocks vorkommt

### Evidence

- src/discover_swiss_mcp/config.py:23 and client.py:154-171 — endpoint inventory: /search, /vertices/{id}, /status, 14 list collections (5 used by the fallback, tools.py:749-755)
- tests/test_live.py:127-340 — live tests cover /search (via all search tools) and /vertices (test_detail_description_is_plain_text); none covers /status or any list endpoint
- probes/PROBE_OPEN_discover-swiss.md:16-27 — the 15-field LIST_SELECT was verified on /lodgingbusinesses, /civicStructures, /webcams only; fallback also reads /places, /foodEstablishments, /localbusinesses
- src/discover_swiss_mcp/client.py:123-126 — own comment: 'a field that is fine on /lodgingbusinesses can 400 on /webcams, and a 400 here fails the whole page'
- tests/conftest.py:36 — mocks registered against the constant-derived PINNED_BASE

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:23 and client.py:154-171 — endpoint inventory: /search, /vertices/{id}, /status, 14 list collections (5 used by the fallback, tools.py:749-755)
- tests/test_live.py:127-340 — live tests cover /search (via all search tools) and /vertices (test_detail_description_is_plain_text); none covers /status or any list endpoint
- probes/PROBE_OPEN_discover-swiss.md:16-27 — the 15-field LIST_SELECT was verified on /lodgingbusinesses, /civicStructures, /webcams only; fallback also reads /places, /foodEstablishments, /localbusinesses
- src/discover_swiss_mcp/client.py:123-126 — own comment: 'a field that is fine on /lodgingbusinesses can 400 on /webcams, and a 400 here fails the whole page'
- tests/conftest.py:36 — mocks registered against the constant-derived PINNED_BASE

**Geschlossen**
- Mocks are bound to the constant (criterion 2 met), but coverage is incomplete (fallback endpoints, /status), three fallback endpoints were never checked with the current select, and nothing live has run.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein `respx`-Mock wird gegen die eigene Konstante registriert:

### Remediation

Add a parametrised @pytest.mark.live contract canary over /status and each FALLBACK_ENDPOINTS entry with top=1 and LIST_SELECT, asserting status != 404 (fail) and 5xx (xfail/skip), and run it once now.

**Disposition:** Add live canaries for /status and for the list endpoints of the fallback (/places, /foodEstablishments, /localbusinesses, /civicStructures, /lodgingbusinesses) with the current select.

### Effort Estimate

S

### Dependencies / Blockers

Live-Lauf braucht einen Key; läuft lokal wie OPS-001.

### Verification After Fix

- Re-Audit von `DRIFT-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
