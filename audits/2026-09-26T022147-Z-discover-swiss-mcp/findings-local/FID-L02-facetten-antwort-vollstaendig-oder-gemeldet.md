## Finding: FID-L02 — Facetten-Antwort vollständig oder gemeldet

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-L02` |
| **PDF-Reference** | — |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

> Serverspezifischer Check. Verengt: FID-006 (Antwortstruktur und Feldnamen bestätigen) — angewandt auf die Facetten-Keys

### Observed Behavior

- resolve_area (client.py:1023-1032) ignores result.missing_facets: a dropped containedInPlace/id facet is reported as 'matched no area at all' in find_tours, find_events, webcams_near and explore_area(region=...) — exactly the 'missing facet appears as no values' case
- AreaLookup (client.py:362-379) has no field to carry the missing facet; no test covers this path

### Expected Behavior

- Keine angefragte Facette verschwindet ohne Eintrag in `missing_facets` + `hint`.
- Ein Test belegt es mit einer Antwort, in der eine Facette fehlt.

### Evidence

- src/discover_swiss_mcp/client.py:207-220 — partition_facet_names: only VERIFIED_FACETS are sent, unknown names returned separately
- src/discover_swiss_mcp/client.py:851-863 — response keys compared against requested names -> SearchResult.missing_facets
- src/discover_swiss_mcp/tools.py:2249-2274 — explore_area: missing_facets = unknown + upstream-missing, with UNKNOWN_FACETS_HINT / MISSING_FACETS_HINT
- tests/test_tools_p3.py:419-449 — unknown not sent; sent-but-missing reported
- tests/test_live.py:275-288 — live canary containedInPlace/id comes back (unexecuted)
- Runtime probe (scratchpad, respx): /search answering facets={} to resolve_area -> find_tours(region='Glarnerland') returns area.identifier=None, hint 'No area is named exactly «Glarnerland». The search text matched no area at all.', no missing_facets; control: explore_area with same answer reports missing_facets=['leafType'] + hint

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:207-220 — partition_facet_names: only VERIFIED_FACETS are sent, unknown names returned separately
- src/discover_swiss_mcp/client.py:851-863 — response keys compared against requested names -> SearchResult.missing_facets
- src/discover_swiss_mcp/tools.py:2249-2274 — explore_area: missing_facets = unknown + upstream-missing, with UNKNOWN_FACETS_HINT / MISSING_FACETS_HINT
- tests/test_tools_p3.py:419-449 — unknown not sent; sent-but-missing reported
- tests/test_live.py:275-288 — live canary containedInPlace/id comes back (unexecuted)
- Runtime probe (scratchpad, respx): /search answering facets={} to resolve_area -> find_tours(region='Glarnerland') returns area.identifier=None, hint 'No area is named exactly «Glarnerland». The search text matched no area at all.', no missing_facets; control: explore_area with same answer reports missing_facets=['leafType'] + hint

**Geschlossen**
- explore_area fulfils the check completely; resolve_area, which the check names explicitly, loses the missing-facet signal.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: discover.swiss verwirft falsch geschriebene Facetten-Namen **still**
(Fundstück 8) — und beantwortet einen erfundenen Namen mit 400 für den ganzen
Request (P3-Stop-Gate). Jede angefragte Facette muss deshalb in der Antwort
stehen oder in `missing_facets` gemeldet werden; eine fehlende Facette darf nie
als «keine Werte» erscheinen.

### Remediation

In resolve_area raise (or return a lookup with hint) when 'containedInPlace/id' is in result.missing_facets, e.g. 'area facet did not come back — this is not an unknown area'; propagate it to the envelopes; add a unit test with facets={}.

**Disposition:** resolve_area ignores missing_facets: a dropped containedInPlace/id facet reads as 'matched no area'. Report it as degraded with the facet named.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-L02` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
