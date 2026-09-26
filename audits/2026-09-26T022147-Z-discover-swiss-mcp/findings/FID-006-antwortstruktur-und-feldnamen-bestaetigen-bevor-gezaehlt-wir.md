## Finding: FID-006 — Antwortstruktur und Feldnamen bestätigen, bevor gezählt wird

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-006` |
| **PDF-Reference** | Custom (Portfolio-Fundstücke MCP Registry 2026-07 und zh-education-mcp / BISTA 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Root paths (values, data, facets) are not confirmed; a structural change becomes a valid empty result with the wildcard-style empty hint
- Fields read from hits (identifier, name, dataGovernance.origin, address.addressLocality, geo, lastModified) are never confirmed on the first entry
- No structure error type; error messages cannot name the keys that actually arrived
- No test holds structure/field names against a real response (live canaries unexecuted; unit fixtures come from recorded probes, which pin the 2026-09 shape but not today's)

### Expected Behavior

- [ ] Der Wurzelpfad der Antwort wird bestätigt, bevor gezählt wird — kein `.get(<Wurzelschlüssel>, [])`, das eine Strukturabweichung in eine Leermenge umschreibt
- [ ] Die vom Code **gelesenen** Felder werden auf dem ersten Eintrag bestätigt, nicht nur die Hülle darum
- [ ] Eine Abweichung endet in einem eigenen Fehlertyp (`UpstreamSchemaError` o. ä.), nicht in einem gültigen leeren Result
- [ ] Die Fehlermeldung nennt die **tatsächlich vorhandenen** Schlüssel — ohne sie ist der nächste Schritt Raten
- [ ] Die Prüfung deckt ausschliesslich, was der Code anfasst; ein zusätzliches optionales Feld upstream lässt sie grün
- [ ] Kein Feldzugriff im Code trägt eine Schreibweise, die die Quelle bereits gewechselt hat, und Endpunkte derselben Quelle mit **unterschiedlicher** Schreibweise werden nicht mit je einem eigenen Literal bedient
- [ ] Hält die Quelle ihre Schreibweise nicht stabil, wird sie an **genau einer** Stelle normalisiert — dort, wo die Rohzeile entsteht, nicht verstreut an den Lesestellen; die Funktion begründet im Docstring, **warum** sie existiert, sonst wird sie beim nächsten Refactoring wegoptimiert
- [ ] Normalisiert wird nur die **Schreibweise**, nicht die Identität des Namens — `anzahl_total` und `anzahlTotal` bleiben verschieden
- [ ] Mindestens ein Test hält Struktur **und** Feldnamen gegen die **echte** Antwort, nicht gegen ein Fixture (`DRIFT-004`, `OPS-009`)
- [ ] **Gegenprobe:** Der Strukturtest ist einmal gegen eine um eine Ebene verschobene Antwort gelaufen und hat dort angeschlagen; wird normalisiert, ist er zusätzlich gegen die jeweils andere Schreibweise gelaufen und hat die Zeile dort gefunden

### Evidence

- src/discover_swiss_mcp/client.py:848-850 — `payload = payload if isinstance(payload, dict) else {}`; facets likewise default to {}
- src/discover_swiss_mcp/client.py:858-861 — `values` defaults to [] when the key is missing or not a list
- src/discover_swiss_mcp/client.py:947-950 — list endpoints: `data` defaults to [] silently
- src/discover_swiss_mcp/client.py:483-490 — facet_values returns [] for an absent facet
- grep SchemaError|UpstreamSchema|UnexpectedPayload|StructureError in src/ — no hits (negative control: pattern fires on 'class UpstreamSchemaError')
- Runtime probe (scratchpad, respx): /search answering {'count':53,'value':[...]} (root key shifted) -> search_impl returns returned=0, upstream_count=53, degraded=None, hint 'No hit. Try: ...' (the FID-003 empty hint); control with 'values' returns 1 hit
- src/discover_swiss_mcp/client.py:896-899 — get_vertex does reject a non-object payload (only confirmation present)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:848-850 — `payload = payload if isinstance(payload, dict) else {}`; facets likewise default to {}
- src/discover_swiss_mcp/client.py:858-861 — `values` defaults to [] when the key is missing or not a list
- src/discover_swiss_mcp/client.py:947-950 — list endpoints: `data` defaults to [] silently
- src/discover_swiss_mcp/client.py:483-490 — facet_values returns [] for an absent facet
- grep SchemaError|UpstreamSchema|UnexpectedPayload|StructureError in src/ — no hits (negative control: pattern fires on 'class UpstreamSchemaError')
- Runtime probe (scratchpad, respx): /search answering {'count':53,'value':[...]} (root key shifted) -> search_impl returns returned=0, upstream_count=53, degraded=None, hint 'No hit. Try: ...' (the FID-003 empty hint); control with 'values' returns 1 hit
- src/discover_swiss_mcp/client.py:896-899 — get_vertex does reject a non-object payload (only confirmation present)

**Geschlossen**
- The recorded-probe fixtures are good, but the reader silently defaults on every root path; the runtime probe shows a shifted payload surfacing as 'No hit' with upstream_count 53. Criterion 5 (only what is touched) and case normalisation are moot since nothing is confirmed. Advisory check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Belegfall (MCP Registry, 2026-07).** Eine Abfrage lieferte konsequent nichts. Die Anfrage war einwandfrei, die Antwort ebenso — nur liegen die gesuchten Felder unter `servers[].server.*`, und gelesen wurde eine Ebene höher. Der Code war syntaktisch fehlerfrei und semantisch blind:

### Remediation

Add UpstreamSchemaError; in search()/list_endpoint() require 'values'/'data' (and 'facets' when facets were requested) and confirm identifier+name on values[0], raising with sorted(payload) keys; map it to a ToolError in server._fail; add a unit test with a shifted payload and a live structure canary.

**Disposition:** Confirm the root paths values/data/facets; a missing root key becomes a structural error (degraded: upstream_shape_changed), never an empty result.

### Effort Estimate

S

### Dependencies / Blockers

Neuer degraded-Wert braucht Envelope-Doku (models.py) und Tool-Hash-Update.

### Verification After Fix

- Re-Audit von `FID-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
