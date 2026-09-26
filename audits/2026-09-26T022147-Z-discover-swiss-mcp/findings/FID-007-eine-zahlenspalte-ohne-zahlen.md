## Finding: FID-007 — Eine Zahlenspalte ohne Zahlen

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-007` |
| **PDF-Reference** | Custom (Portfolio-Fundstück zh-education-mcp / BISTA, 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- List fallback with `near`: rows whose geo is missing/non-numeric are dropped without a counter; upstream_count (tools.py:1020) is computed after the drop, so the result cannot say how many were excluded or in which direction the count deviates (the 'except ValueError: continue' anti-pattern)
- No live test of which non-numeric values the source actually uses in numeric fields

### Expected Behavior

- [ ] Jede Konvertierung eines Quellwerts in eine Zahl kennt den Fall «keine Zahl» und behandelt ihn ausdrücklich
- [ ] Eine unterdrückte Zelle wird **nicht** zu `0` — weder durch `or 0` noch durch einen `.get(…, 0)`-Default noch durch ein stillschweigendes `except`
- [ ] Eine unterdrückte Zelle bricht den Aufruf **nicht** ab; sie wird ausgenommen
- [ ] Das Tool-Result **nennt** die Zahl der ausgenommenen Zeilen — ohne sie ist die Summe von einer vollständigen nicht zu unterscheiden
- [ ] Der Hinweis sagt, in welche Richtung die Summe abweicht («die echten Werte liegen höher»), nicht nur, dass etwas fehlt
- [ ] Die bekannten Marker der Quelle sind an einer Stelle benannt, nicht über die Lesestellen verstreut
- [ ] Ein Live-Test hält die tatsächlich vorkommenden Nicht-Zahlen gegen diese Liste — welche Marker eine Quelle benutzt, weiss nur die Quelle
- [ ] **Gegenprobe:** Die stille Variante ist einmal danebengestellt worden und liefert dieselbe Zahl. Wer das nicht gezeigt hat, hält den Hinweis für Kosmetik

### Evidence

- src/discover_swiss_mcp/tools.py:546-553 — _int_or_none: non-integers become None, never 0
- src/discover_swiss_mcp/tools.py:1240-1242, 1439-1443 — stars and length converted only when numeric, else None
- src/discover_swiss_mcp/tools.py:2195 and client.py:479 — facet counts: int or None, not 0
- src/discover_swiss_mcp/client.py:552-571 — totals read only when int
- src/discover_swiss_mcp/client.py:519-523 — filter_by_distance: `except (KeyError, TypeError, ValueError): continue` drops rows with non-numeric coordinates, uncounted

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:546-553 — _int_or_none: non-integers become None, never 0
- src/discover_swiss_mcp/tools.py:1240-1242, 1439-1443 — stars and length converted only when numeric, else None
- src/discover_swiss_mcp/tools.py:2195 and client.py:479 — facet counts: int or None, not 0
- src/discover_swiss_mcp/client.py:552-571 — totals read only when int
- src/discover_swiss_mcp/client.py:519-523 — filter_by_distance: `except (KeyError, TypeError, ValueError): continue` drops rows with non-numeric coordinates, uncounted

**Geschlossen**
- The server computes no sums of source values, and every numeric conversion maps non-numbers to None rather than 0. The only silent exclusion is the fallback distance filter. Criteria on suppression-marker lists and the counter-probe are not applicable (the source has no suppression markers). Advisory check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Amtliche Quellen unterdrücken kleine Fallzahlen aus Datenschutzgründen. Statt der Zahl steht dann ein Bereich, ein Vergleich oder ein Platzhalter: `1 bis 5`, `<5`, `NULL`, `k.A.`, `*`, die leere Zelle. Die Spalte heisst weiterhin «Anzahl», ihr Typ ist weiterhin «Zahl» — nur ein Teil der Zellen ist keine.

### Remediation

Count rows dropped for missing/invalid coordinates in _scan_lists and expose it (e.g. applied['rows_without_coordinates']) with a hint that they are not in the result.

**Disposition:** The list fallback drops rows with missing or invalid geo without counting them; add excluded_without_geo.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
