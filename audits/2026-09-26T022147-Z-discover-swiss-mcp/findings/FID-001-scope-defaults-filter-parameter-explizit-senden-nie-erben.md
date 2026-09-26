## Finding: FID-001 — Scope-Defaults: Filter-Parameter explizit senden, nie erben

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-001` |
| **PDF-Reference** | Custom (Portfolio-Fundstück termdat-mcp#11) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Default-Matrix is hand-written, not derived from the spec: FacetRequest members (count/scope/project), includeAllPhotos on /vertices, Accept-Timezone are missing; completeness over all optional params of the used endpoints is not shown
- Recall delta for list `project` (undocumented partner default) was not measured, only 'works without'
- resolve_area requests the containedInPlace/id facet with count=30 (client.py:1028); an exact area name ranked beyond the top 30 is reported as 'No area is named exactly' (client.py:1079) — the truncation is not visible in the result
- Live canaries (tests/test_live.py) that would re-measure recall have never been executed; empirical evidence is the 2026-09-17 probe only
- Accept-Language header is not regression-tested

### Expected Behavior

- [ ] Default-Matrix existiert und deckt **alle** optionalen Parameter der genutzten Endpoints ab
- [ ] Jeder Parameter mit einschränkendem Default wird vom Server explizit gesetzt
- [ ] Das Recall-Delta (weggelassen vs. explizit maximal) ist für jeden solchen Parameter empirisch gemessen und dokumentiert
- [ ] Eine bewusst gewählte Einschränkung ist im Tool-Result sichtbar (Feld oder `hint`), nicht nur im README
- [ ] Ein Regressionstest hält den vollen Scope fest (siehe FID-002)
- [ ] Scheitert die Ermittlung des vollen Scopes zur Laufzeit (z. B. Vokabular-Endpoint nicht erreichbar), degradiert der Server sauber — die Erweiterung darf die Suche nie brechen

### Evidence

- probes/PROBE_REPORT_discover-swiss-mcp.md:70-89 — Default-Matrix (top, project list/search, Accept-Language, categoryVersion, select, datasource, updatedSince, deleted, resultsPerPage, facets[].name, searchFields) with measured values (top 10/5/1000, resultsPerPage default 10, searchFields 53/7/15)
- src/discover_swiss_mcp/client.py:822-830 — /search always sends project as array and select; project re-imposed after caller body
- src/discover_swiss_mcp/client.py:932-944 — list endpoints always send project, top=200 (overridden to 1000 by fallback), select, includeCount on first page
- src/discover_swiss_mcp/client.py:660-666 — Accept-Language and categoryVersion always explicit
- src/discover_swiss_mcp/tools.py:1050-1052, 1212-1214, 1425-1427 — resultsPerPage/currentPage explicit on every search body
- src/discover_swiss_mcp/tools.py:492, 1059-1060 — `applied` field in every paged response carries the scope actually sent (incl. default_type_exclusion)
- tests/test_client.py:45-64, tests/test_tools.py:195-205, tests/test_tools_p3.py:630-631, tests/test_client.py:163-166 — regression tests hold project, resultsPerPage, select, top=1000, includeCount
- Spec extraction (probes/probe_out/openapi.json, run in this audit) — optional params of POST /search FacetRequest (count, scope default 'current', project), /vertices/{id} includeAllPhotos ('otherwise images with low confidence will be skipped'), Accept-Timezone header are not in the matrix

### Gemessen / Geschlossen / Offen

**Gemessen**
- probes/PROBE_REPORT_discover-swiss-mcp.md:70-89 — Default-Matrix (top, project list/search, Accept-Language, categoryVersion, select, datasource, updatedSince, deleted, resultsPerPage, facets[].name, searchFields) with measured values (top 10/5/1000, resultsPerPage default 10, searchFields 53/7/15)
- src/discover_swiss_mcp/client.py:822-830 — /search always sends project as array and select; project re-imposed after caller body
- src/discover_swiss_mcp/client.py:932-944 — list endpoints always send project, top=200 (overridden to 1000 by fallback), select, includeCount on first page
- src/discover_swiss_mcp/client.py:660-666 — Accept-Language and categoryVersion always explicit
- src/discover_swiss_mcp/tools.py:1050-1052, 1212-1214, 1425-1427 — resultsPerPage/currentPage explicit on every search body
- src/discover_swiss_mcp/tools.py:492, 1059-1060 — `applied` field in every paged response carries the scope actually sent (incl. default_type_exclusion)
- tests/test_client.py:45-64, tests/test_tools.py:195-205, tests/test_tools_p3.py:630-631, tests/test_client.py:163-166 — regression tests hold project, resultsPerPage, select, top=1000, includeCount
- Spec extraction (probes/probe_out/openapi.json, run in this audit) — optional params of POST /search FacetRequest (count, scope default 'current', project), /vertices/{id} includeAllPhotos ('otherwise images with low confidence will be skipped'), Accept-Timezone header are not in the matrix

**Geschlossen**
- Every restricting default the probe found (top, project, resultsPerPage, select, facet names) is sent explicitly and pinned by unit tests; the sent scope is exposed in `applied`. The matrix is not shown to be complete against the spec, one deliberate truncation (area facet count 30) is invisible, and no live re-measurement has run. Criterion 6 (scope-widening fallback) not applicable: no vocabulary-based widening.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein optionaler Query-Parameter, dessen Weglassen **nicht** «unbeschränkt» bedeutet, sondern einen willkürlichen Teilausschnitt. Der Server sendet den Parameter nicht, die Upstream-API setzt einen Default, und der Server durchsucht ohne es zu merken einen Bruchteil der Datenbank. Die Antwort ist syntaktisch korrekt, HTTP 200, wohlgeformtes JSON — und inhaltlich falsch.

### Remediation

Generate the Default-Matrix from probes/probe_out/openapi.json for /search (incl. FacetRequest), /vertices/{id} and the list endpoints and add the missing rows; when resolve_area finds no exact match among the 30 facet values, say in the hint that only the top 30 areas by content were compared (or page the facet); add a test for Accept-Language; run tests/test_live.py once with a key and record the values.

**Disposition:** Derive the default matrix from the spec for the members still unpinned (FacetRequest count/scope, includeAllPhotos on /vertices, Accept-Timezone) and state the facet value limit (count=30) used by resolve_area in the result.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-001` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
