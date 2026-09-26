## Finding: FID-002 — Recall-Ground-Truth: Referenzqueries gegen die offizielle Oberfläche

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-002` |
| **PDF-Reference** | Custom (Portfolio-Fundstück termdat-mcp#11) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- The only web-UI comparison (zuerich.com) was made against list endpoints (datasource=zht-cms), not against the /search query endpoint the tools use
- Reference queries (Landesmuseum, Grindelwald, Wanderung) have API counts only; no UI count at the same time, so no per-query delta exists
- Live recall canaries exist but have never been executed (no key in CI, not run locally per task brief) — per §2.6 this is todo, not evidence
- No canary for the zht-cms ground-truth total (probe report line 135 proposes 'datasource=zht-cms gesamt >= 1200'; test_live.py:225-236 uses sourcePartner facet >= 600 instead)

### Expected Behavior

- [ ] 3–5 Referenzqueries definiert, die den typischen Nutzungsfall abdecken (nicht nur den Anchor-Demo-Query)
- [ ] Trefferzahlen beider Oberflächen zum selben Zeitpunkt gemessen und dokumentiert
- [ ] Jedes Delta ist erklärt — Zählweise, Kürzung, Sprachraum, Feldabdeckung
- [ ] Recall-Regressionstest mit Untergrenzen existiert und läuft unter `@pytest.mark.live`
- [ ] Der Vergleich deckt **Query-/Such-Endpoints** ab, nicht nur Listen-Endpoints
- [ ] Bei Servern ohne offizielles Web-UI: dokumentierte Ersatz-Ground-Truth (Bulk-Dump-Zeilenzahl, veröffentlichte Bestandszahlen)

### Evidence

- probes/PROBE_REPORT_discover-swiss-mcp.md:128-135 — Ground truth zuerich.com 1'481 vs API datasource=zht-cms 1'596, delta +8 % explained (curated categories, region, camping)
- probes/PROBE_REPORT_discover-swiss-mcp.md:93-98, 193 — reference counts Landesmuseum 53, Grindelwald 37, Wanderung 529, hotels 3'093, tours 223, webcams 73
- probes/PROBE_OPEN_discover-swiss.md:9-12 — list vs search cross-check: /tours Glarnerland 117 = 117, /civicStructures Zürich 232 = 232
- tests/test_live.py:127-247 — recall floors (about half of measured) under pytestmark live (test_live.py:60) for search, find_accommodation, find_tours, webcams_near, explore_area, find_events, sourcePartner=zht
- tests/test_live.py:116 — _assert_live refuses a degraded answer as a measurement

### Gemessen / Geschlossen / Offen

**Gemessen**
- probes/PROBE_REPORT_discover-swiss-mcp.md:128-135 — Ground truth zuerich.com 1'481 vs API datasource=zht-cms 1'596, delta +8 % explained (curated categories, region, camping)
- probes/PROBE_REPORT_discover-swiss-mcp.md:93-98, 193 — reference counts Landesmuseum 53, Grindelwald 37, Wanderung 529, hotels 3'093, tours 223, webcams 73
- probes/PROBE_OPEN_discover-swiss.md:9-12 — list vs search cross-check: /tours Glarnerland 117 = 117, /civicStructures Zürich 232 = 232
- tests/test_live.py:127-247 — recall floors (about half of measured) under pytestmark live (test_live.py:60) for search, find_accommodation, find_tours, webcams_near, explore_area, find_events, sourcePartner=zht
- tests/test_live.py:116 — _assert_live refuses a degraded answer as a measurement

**Geschlossen**
- 3-5 reference queries with floors at half the measured value exist and cover query endpoints; one UI ground truth with an explained delta exists but on list endpoints. The query-level UI comparison and any execution of the canaries are missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein MCP-Server ist eine zweite Oberfläche auf einen Bestand, für den es bereits eine erste gibt: das offizielle Web-UI der Datenquelle. Diese erste Oberfläche ist die einzige verfügbare Ground Truth. Wer sie nicht abfragt, hat kein Mittel festzustellen, ob der Server liefert, was die Quelle hat.

### Remediation

Measure 3 reference queries on the discover.swiss/zuerich.com UI and via search_impl on the same day, record the delta table in README Known limitations, and run `pytest -m live -rA` once; keep the output with the audit.

**Disposition:** Web-UI ground truth exists only for list endpoints (zuerich.com vs datasource zht-cms, +8 %). Add one UI-count comparison against /search for the anchor queries.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
