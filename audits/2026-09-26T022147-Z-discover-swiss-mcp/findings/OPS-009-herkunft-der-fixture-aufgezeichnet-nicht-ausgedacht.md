## Finding: OPS-009 — Herkunft der Fixture: aufgezeichnet, nicht ausgedacht

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-009` |
| **PDF-Reference** | Custom (Katalog-Lücke gegen mcp-data-fidelity-skill, 2026-08-07) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- 43 hand-written json_response({...}) literals in tests shape external endpoints (e.g. tests/test_client.py:49, 135, 159, 213, 227, 362) rather than constructing out-of-source edge cases
- No live test compares a recorded fixture's field set against the live source (test_live.py canaries check counts/floors only)
- No counter-test showing an invented response would be rejected by such a comparison
- The re-record path is implicit (scripts in probes/); CONTRIBUTING.md:16-20 says the probe is the truth but gives no command to refresh

### Expected Behavior

- [ ] Für **jeden** externen Endpunkt liegt mindestens eine Fixture vor, die von der echten Quelle stammt
- [ ] Jede solche Fixture trägt ein **Aufnahmedatum** — im Dateinamen, im Dateikopf oder in einer `PROVENANCE`-Datei daneben
- [ ] Die Herkunft nennt den **Endpunkt**, gegen den aufgenommen wurde, nicht nur «die API»
- [ ] Es gibt einen dokumentierten Weg, die Aufnahme zu **wiederholen** — ein Skript oder ein Befehl, nicht eine Erinnerung
- [ ] Antwort-Literale im Testcode stellen keinen externen Endpunkt dar; wo sie stehen, konstruieren sie einen Grenzfall, den die Quelle nicht liefert
- [ ] Ein Live-Test hält mindestens eine Aufnahme gegen die Quelle — auf der Ebene der Felder, die der Code liest
- [ ] **Gegenprobe:** Eine erfundene Antwort ist einmal danebengehalten worden und hat sich von der Aufnahme unterschieden. Ohne sie belegt der Vergleich nur, dass zwei Dateien gleich sind

### Evidence

- tests/conftest.py:109-111 — probe_fixture() loads recorded upstream responses from probes/ ('The probes are the reference, not a mock')
- Recorded fixtures used in tests: /search (probes/probe_out/search_dsod-content_1.json, _4.json; probe_verify_out/f1_odata.json, f5_facet.json, f3_webcam_sg.json), /vertices (probe_detail_out/detail_civic_landesmuseum.json, detail_hotel_interlaken.json), list endpoints (probe_out/raw_first_page_dsod-content_accommodations.json, probe_open_out/select_row_webcams.json)
- probes/PROBE_VERIFY_discover-swiss.md:3, PROBE_DETAIL_discover-swiss.md:3, PROBE_OPEN_discover-swiss.md:3, PROBE_REPORT_discover-swiss-mcp.md:3 — recording date per probe run (2026-09-17 / 2026-09-23) and base URL
- probes/probe_verify.py:30-52 — recording script writes request body, status and response per file; probe_open.py, probe_detail.py, probe_license.py, probe_tour_kinds.py likewise
- /status is only ever 204 without body; tests mock httpx.Response(204) (tests/test_client.py:464,474)

### Gemessen / Geschlossen / Offen

**Gemessen**
- tests/conftest.py:109-111 — probe_fixture() loads recorded upstream responses from probes/ ('The probes are the reference, not a mock')
- Recorded fixtures used in tests: /search (probes/probe_out/search_dsod-content_1.json, _4.json; probe_verify_out/f1_odata.json, f5_facet.json, f3_webcam_sg.json), /vertices (probe_detail_out/detail_civic_landesmuseum.json, detail_hotel_interlaken.json), list endpoints (probe_out/raw_first_page_dsod-content_accommodations.json, probe_open_out/select_row_webcams.json)
- probes/PROBE_VERIFY_discover-swiss.md:3, PROBE_DETAIL_discover-swiss.md:3, PROBE_OPEN_discover-swiss.md:3, PROBE_REPORT_discover-swiss-mcp.md:3 — recording date per probe run (2026-09-17 / 2026-09-23) and base URL
- probes/probe_verify.py:30-52 — recording script writes request body, status and response per file; probe_open.py, probe_detail.py, probe_license.py, probe_tour_kinds.py likewise
- /status is only ever 204 without body; tests mock httpx.Response(204) (tests/test_client.py:464,474)

**Geschlossen**
- 4 of 7 criteria met. Fixture provenance is unusually good (dated probe runs, scripts that recorded them, tests load them); missing is the live field-level drift test and the removal of skeleton literals for real endpoints.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein handgeschriebener Mock kodiert die Annahme seines Autors. Er kann sie deshalb **prinzipiell** nicht widerlegen: Produktivcode und Fixture stammen aus demselben Kopf, zur selben Stunde, aus derselben Lektüre der Dokumentation. Wo beide irren, irren beide gleich — und die Suite bleibt dauerhaft grün.

### Remediation

Add a live test that loads e.g. probe_out/search_dsod-content_1.json and asserts set(recorded values[0]) == set(live values[0]) on the fields tools.py reads, plus an offline counter-test with an invented payload; document 'python probes/probe_verify.py' as the refresh path in CONTRIBUTING; replace endpoint-shaped literals with trimmed recorded payloads where they stand for real answers.

**Disposition:** Replace the most important of the 43 hand-written upstream payloads with recorded probe responses.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-009` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
