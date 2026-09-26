## Finding: OBS-008 — Der Server sagt an, dass er bedient — eine stabile Zeile auf stderr

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-008` |
| **PDF-Reference** | Custom (Portfolio-Erhebung 2026-08-03, 42 veröffentlichte Server) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Marker is not documented in README.md/README.de.md: grep -niE 'marker|bereitschaft|ready|lifespan started' finds only unrelated hits (README.md:231, 269) — criterion 'documented in README in the compared spelling' not met
- With closed stdin the process exits 0 after the marker instead of staying up (check expects exit 124); marker still appears within 6 s

### Expected Behavior

- [ ] Der Server schreibt beim Erreichen des Bedienzustands eine Zeile auf **stderr**, nicht auf stdout (`OBS-003`)
- [ ] Die Zeile erscheint innerhalb von sechs Sekunden bei **geschlossenem stdin**, ohne dass eine Anfrage gestellt wurde
- [ ] Bei strukturiertem Log ist das `event`- bzw. `msg`-Feld **exakt** der Marker — erklärende Zusätze stehen in eigenen Feldern
- [ ] Bei Klartext-Log ist eine **stabile Teilzeichenkette** als Marker benannt
- [ ] Der Marker enthält **keinen Zeitstempel** und nichts anderes Laufvariables (PID, Port, Dauer, konfigurationsabhängige Anzahlen)
- [ ] Der Marker stammt aus dem Code des Servers — der **SDK-Banner zählt nicht**
- [ ] Alles, was scheitern kann (Konfiguration, Clients, Tool-Registrierung), liegt **vor** dem Marker
- [ ] Der Marker ist im README dokumentiert, in der Schreibweise, auf die verglichen wird
- [ ] Die negative Kontrolle wurde durchgeführt: ein erzwungener Fehlstart erzeugt Ausgabe auf stderr — sonst misst der Aufbau nichts

### Evidence

- src/discover_swiss_mcp/server.py:117-134 — settings load, client construction and server.list_tools() happen before logger.info('Server lifespan started', ...); explanatory data in separate fields
- runtime: stdin held open (sleep 8 | timeout 6 python -m discover_swiss_mcp) -> exit 124, stderr: {"...", "event": "Server lifespan started", "level": "info", "timestamp": ...}; stdout 0 bytes
- runtime: stdin=/dev/null -> marker line, then 'Server lifespan stopped', exit 0 (clean EOF shutdown, not a crash)
- negative control: DISCOVER_SWISS_MCP_TRANSPORT=bogus and DISCOVER_SWISS_MCP_PORT=abc -> ConfigError traceback on stderr (measurement setup lets output through)
- tests/test_smoke.py:71-84 — exact equality on event == 'Server lifespan started' asserted
- No SDK banner on stderr; marker has no timestamp/PID/port inside the event field

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:117-134 — settings load, client construction and server.list_tools() happen before logger.info('Server lifespan started', ...); explanatory data in separate fields
- runtime: stdin held open (sleep 8 | timeout 6 python -m discover_swiss_mcp) -> exit 124, stderr: {"...", "event": "Server lifespan started", "level": "info", "timestamp": ...}; stdout 0 bytes
- runtime: stdin=/dev/null -> marker line, then 'Server lifespan stopped', exit 0 (clean EOF shutdown, not a crash)
- negative control: DISCOVER_SWISS_MCP_TRANSPORT=bogus and DISCOVER_SWISS_MCP_PORT=abc -> ConfigError traceback on stderr (measurement setup lets output through)
- tests/test_smoke.py:71-84 — exact equality on event == 'Server lifespan started' asserted
- No SDK banner on stderr; marker has no timestamp/PID/port inside the event field

**Geschlossen**
- 8 of 9 criteria met; the ready marker is correct in form and position and pinned by an exact-equality test, but it is not a documented contract.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein MCP-Server auf stdio hat einen Moment, in dem sich alles entscheidet: Er hat seine Konfiguration gelesen, seine Clients gebaut, seine Tools registriert — und wartet ab jetzt auf Anfragen. Vor diesem Moment ist er ein Prozess, danach ist er ein Server. Von aussen sind beide Zustände dasselbe: eine PID, die nichts tut.

### Remediation

Add one line to both READMEs: 'Ready marker (stderr, JSON field `event`): `Server lifespan started`'.

**Disposition:** Document the readiness marker 'Server lifespan started' in both READMEs.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
