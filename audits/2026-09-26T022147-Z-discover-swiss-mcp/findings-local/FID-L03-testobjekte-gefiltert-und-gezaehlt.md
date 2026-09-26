## Finding: FID-L03 — Testobjekte gefiltert und gezählt

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-L03` |
| **PDF-Reference** | — |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

> Serverspezifischer Check. Verengt: FID-003 (Leermenge unterscheidbar) — Filterung ohne Zähler wäre eine stille Verkleinerung

### Observed Behavior

- get_details (tools.py:1156) applies only is_servable, not is_test_object: a test record fetched by identifier is delivered in full and not counted
- is_test_object checks obj.email and address.email but not organizer.email, where the recorded Demo Event carries mail@example.ch (tests/test_licenses.py:226) — detection there relies on the name alone

### Expected Behavior

- Filter greift in jedem Tool, das Objekte ausliefert, und zählt.
- Test mit dem aufgezeichneten Objekt vorhanden.

### Evidence

- src/discover_swiss_mcp/licenses.py:57-63, 195-226 — detection rules: name word-boundary demo|test|beispiel|muster|placeholder, placeholder street/PLZ/Ort, example.ch/.com mail
- src/discover_swiss_mcp/licenses.py:253-255 — screen() counts excluded_test_objects; applied in all search-based tools and both fallbacks (tools.py:992, 1075, 1268, 1356, 1512, 1816, 2031)
- tests/test_licenses.py:220-271 — demo event recognised; counter-probe: 'Demokratie-Forum', 'Protestmarsch' etc. stay in
- tests/test_tools_p3.py:82-99, 206-217 — recorded f4_odata.json with Demo Event: excluded_test_objects == 1
- tests/test_live.py:323-340 — live canary excluded_test_objects >= 1, skip at 0 (unexecuted)
- Runtime probe (scratchpad, respx): get_details on a Demo Event object (name 'Demo Event', Strasse 1/PLZ/Ort) -> detail served, excluded_test_objects=0

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/licenses.py:57-63, 195-226 — detection rules: name word-boundary demo|test|beispiel|muster|placeholder, placeholder street/PLZ/Ort, example.ch/.com mail
- src/discover_swiss_mcp/licenses.py:253-255 — screen() counts excluded_test_objects; applied in all search-based tools and both fallbacks (tools.py:992, 1075, 1268, 1356, 1512, 1816, 2031)
- tests/test_licenses.py:220-271 — demo event recognised; counter-probe: 'Demokratie-Forum', 'Protestmarsch' etc. stay in
- tests/test_tools_p3.py:82-99, 206-217 — recorded f4_odata.json with Demo Event: excluded_test_objects == 1
- tests/test_live.py:323-340 — live canary excluded_test_objects >= 1, skip at 0 (unexecuted)
- Runtime probe (scratchpad, respx): get_details on a Demo Event object (name 'Demo Event', Strasse 1/PLZ/Ort) -> detail served, excluded_test_objects=0

**Geschlossen**
- Filter and counter work on every list-shaped tool and are tested with the recorded object; the detail tool is the exception.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Produktivindex enthält ein «Demo Event» mit Platzhalteradresse
(Fundstück 10). Der Server muss es herausfiltern **und** in
`excluded_test_objects` zählen: gefiltert ohne Zähler verschweigt, wie dünn
der Bestand ist; ungefiltert empfiehlt er einem Gast den Platzhalter.

### Remediation

In get_details_impl, after the licence gate, return a withheld envelope with excluded_test_objects=1 and a hint when is_test_object(obj); also check organizer.email; add a unit test.

**Disposition:** get_details returns a test object (Demo Event) in full and uncounted. Withhold it there too, with excluded_test_objects=1 and a hint.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-L03` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
