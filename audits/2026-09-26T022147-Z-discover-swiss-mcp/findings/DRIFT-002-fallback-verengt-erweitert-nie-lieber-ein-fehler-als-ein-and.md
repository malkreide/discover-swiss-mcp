## Finding: DRIFT-002 — Fallback verengt, erweitert nie — lieber ein Fehler als ein anderer Datensatz

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-002` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#33, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Fallbacks widen the answer set: search fallback drops `query` (returns everything near the point), accommodation fallback returns hotels regardless of stars/amenities/accessibility
- Which inputs were ignored is stated only in the hint string; `applied` (tools.py:897-917) has no field for ignored query/filters
- _accommodation_fallback and _ignored_accommodation_filters have no test (no test references them)
- tools.py:1724-1734 _schedule_entry falls back to entries[0] when no entry runs on from_date, which the event hit then reports as the overlapping entry; webcams live_url accepts link type 'WebLink' (tools.py:1863), only 'WebDetail' is verified as a live image

### Expected Behavior

- [ ] Jeder Auswahl-Fallback liefert denselben Datensatz-Typ wie der Primärpfad (gleiche Granularität, gleicher Zeitbezug, gleiche Entität)
- [ ] Fallbacks, die die Semantik ändern, sind entweder entfernt oder in der Antwort ausgewiesen (Feld, nicht nur Prosa)
- [ ] Wo kein semantisch gleichwertiger Kandidat existiert, wird eskaliert statt substituiert
- [ ] Ein Test hält fest, dass der Nicht-Fund ein Fehler ist — nicht nur, dass der Fund funktioniert
- [ ] Die Auswahlfunktion begründet im Docstring, was sie bewusst **nicht** nimmt

### Evidence

- src/discover_swiss_mcp/client.py:1035-1092 — resolve_area: exact name only; no exact match -> no id + suggestions; several exact matches -> largest with ambiguous=True and rivals in hint
- src/discover_swiss_mcp/tools.py:1480-1495, 1787-1797, 2004-2014, 2222-2232 — unresolved region: no search is run
- src/discover_swiss_mcp/tools.py:942-965 — search fallback without near/locality fetches nothing
- src/discover_swiss_mcp/tools.py:1013-1016, 1370-1379 — fallback responses carry provenance=list_fallback, degraded=search_unavailable fields; ignored query/filters named in hint prose
- src/discover_swiss_mcp/tools.py:1305-1324 — accommodation fallback ignores stars_min, garni, price_range, amenities, accessible
- tests/test_tools.py:670-681, tests/test_tools_p3.py:659 — tests that the non-find is not a substitution
- src/discover_swiss_mcp/client.py:966-981 — list_fallback docstring: 'Deliberately narrow, and deliberately not to be widened'

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:1035-1092 — resolve_area: exact name only; no exact match -> no id + suggestions; several exact matches -> largest with ambiguous=True and rivals in hint
- src/discover_swiss_mcp/tools.py:1480-1495, 1787-1797, 2004-2014, 2222-2232 — unresolved region: no search is run
- src/discover_swiss_mcp/tools.py:942-965 — search fallback without near/locality fetches nothing
- src/discover_swiss_mcp/tools.py:1013-1016, 1370-1379 — fallback responses carry provenance=list_fallback, degraded=search_unavailable fields; ignored query/filters named in hint prose
- src/discover_swiss_mcp/tools.py:1305-1324 — accommodation fallback ignores stars_min, garni, price_range, amenities, accessible
- tests/test_tools.py:670-681, tests/test_tools_p3.py:659 — tests that the non-find is not a substitution
- src/discover_swiss_mcp/client.py:966-981 — list_fallback docstring: 'Deliberately narrow, and deliberately not to be widened'

**Geschlossen**
- Area resolution escalates correctly and is tested. The search-refused fallback is declared (degraded/provenance fields) but widens semantics with the specifics in prose only, and its accommodation branch is untested.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Resilienz-Fallbacks sind Pflicht (Probe-Skill 3.1/3.5): Retry, Dump statt API, Cache statt Live. Alle diese lockern den **Weg** zum selben Datensatz. Es gibt aber eine zweite, verwandt aussehende Sorte, die etwas ganz anderes tut — sie lockert, **welcher Datensatz** geliefert wird:

### Remediation

Add applied['ignored'] = ['query', 'stars_min', ...] to both fallbacks; add a test for _accommodation_fallback asserting the ignored list; make _schedule_entry return None when no entry overlaps; restrict LIVE_LINK_TYPES to verified types.

**Disposition:** The list fallback widens the answer (search ignores query, accommodation ignores stars/amenities/accessible). Report the ignored inputs as a structured field (ignored_parameters), not only in hint, and test the accommodation fallback.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DRIFT-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
