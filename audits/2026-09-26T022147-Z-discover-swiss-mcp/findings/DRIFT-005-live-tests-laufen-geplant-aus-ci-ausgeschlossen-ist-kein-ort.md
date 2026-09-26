## Finding: DRIFT-005 — Live-Tests laufen geplant — «aus CI ausgeschlossen» ist kein Ort

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-005` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#35, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No scheduled live run and no external auditor reference
- No failure signal (issue/notification)
- No workflow_dispatch entry point for the live suite
- README/CONTRIBUTING name neither cadence nor responsible person

### Expected Behavior

- [ ] Die Live-Suite läuft zeitgesteuert (mindestens wöchentlich) oder ist nachweislich von einem externen Auditor abgedeckt
- [ ] Ein Fehlschlag erzeugt ein sichtbares Signal — Issue, Benachrichtigung oder Report; nicht nur einen roten Lauf im Actions-Tab
- [ ] `workflow_dispatch` ist gesetzt, damit die Suite nach einem Upstream-Hinweis sofort ausführbar ist
- [ ] Der PR-Lauf bleibt bei `-m "not live"` — dieser Check verlangt einen *zusätzlichen* Lauf, keinen Umbau
- [ ] README oder CONTRIBUTING nennt Kadenz und Verantwortliche

### Evidence

- .github/workflows/ci.yml:67 — the only pytest step: `pytest -m "not live"`
- grep schedule|cron in .github/workflows/*.yml — no hit (negative control: pattern fires on a sample 'schedule:/cron:' block); publish.yml has no pytest step
- README.md:287-299 — live canaries documented as local-only ('never in CI'), no cadence, no owner
- tests/test_live.py:1-10 — module docstring: 'CI ... never sees them; locally they run with a key'

### Gemessen / Geschlossen / Offen

**Gemessen**
- .github/workflows/ci.yml:67 — the only pytest step: `pytest -m "not live"`
- grep schedule|cron in .github/workflows/*.yml — no hit (negative control: pattern fires on a sample 'schedule:/cron:' block); publish.yml has no pytest step
- README.md:287-299 — live canaries documented as local-only ('never in CI'), no cadence, no owner
- tests/test_live.py:1-10 — module docstring: 'CI ... never sees them; locally they run with a key'

**Geschlossen**
- Only the 'PR run stays not live' criterion is met; the live suite runs nowhere.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Ausschluss erzeugt allerdings die Blindheit, vor der `OPS-001` warnt. Ein Test, der nirgends läuft, ist Dokumentation, kein Schutz — und er verrottet leise, weil sein Scheitern niemandem auffällt. Genau diese Tests sind aber die einzigen, die eine falsche Grundannahme widerlegen können (`FID-002`, `DRIFT-004`); dass ausgerechnet sie nicht ausgeführt werden, ist die unangenehmste Lücke der Test-Strategie.

### Remediation

Add .github/workflows/live-tests.yml (weekly cron + workflow_dispatch, DISCOVER_SWISS_KEY from repository secrets, `pytest -m live -rA`, issue on failure) and a README paragraph with cadence and owner.

**Disposition:** No scheduled live run: CI deliberately holds no key (bring-your-own-key, 50'000 calls/month on the maintainer's subscription). Live canaries run locally at every phase gate; revisit if a dedicated CI key is issued by discover.swiss.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DRIFT-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
