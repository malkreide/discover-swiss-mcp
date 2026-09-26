## Finding: DRIFT-006 — Der CHANGELOG darf dem Code nicht widersprechen

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | closed |
| **Disposition** | nach dem Audit behoben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-006` |
| **PDF-Reference** | Custom (Portfolio-Fundstück swiss-energy-mcp, 2026-08-01) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- CHANGELOG claims an audit report that is not in the repository
- CHANGELOG overstates live-canary coverage ('all eight tool paths')
- README Known limitation #8 describes the pre-stop-gate behaviour the code comment itself refutes
- Two code comments present unmeasured facts as measured (list select on all fallback endpoints; 429 body wording)

### Expected Behavior

- [ ] Jeder Eintrag in `[Unreleased]` beschreibt Arbeit, die **nicht** auf `main` ist oder noch nicht publiziert wurde
- [ ] Kein Satz in CHANGELOG, README oder Doku bezeichnet als ausstehend, geplant oder ausserhalb des Scopes, was bereits gemergt ist
- [ ] Keine dokumentierte Einschränkung, die der Code nicht mehr hat
- [ ] Keine Docstrings oder Kommentare mit «noch nicht», die der umgebende Code widerlegt
- [ ] Widersprüche wurden **gefunden, indem jede Behauptung geprüft wurde** (Modus 1) — eine leere `grep`-Trefferliste allein ist `not_verified`, nicht Pass
- [ ] Der PR, der eine Absicht ausführt, korrigiert im selben Diff den Satz, der sie als Absicht führt

### Evidence

- CHANGELOG.md:78-79 — '[Unreleased] Added: Audit audits/AUDIT_2026-09-26.md ... and its run directory' — file absent; `git ls-files audits` returns 0 files at bd0e371 (audits/ is untracked)
- CHANGELOG.md:67-70 — 'recall floors ... for all eight tool paths' vs tests/test_live.py:127-247: floors for 6 tools (search, find_accommodation, find_tours, webcams_near, explore_area, find_events) + a client.search partner check; none for get_details or source_status
- README.md:232 — 'Unknown facet names are dropped silently' vs src/discover_swiss_mcp/client.py:210-214 and CHANGELOG.md:109-112/169-171 — an invented name answers HTTP 400; only filterPropertyName spellings are dropped
- src/discover_swiss_mcp/client.py:117-127 — comment 'Fifteen fields, every one of them answered live' vs probes/PROBE_OPEN_discover-swiss.md:16-27 — six of them verified on 3 of the 5 fallback endpoints
- src/discover_swiss_mcp/client.py:534-535 — docstring states the gateway's 429 wording as fact vs probes/PROBE_OPEN_discover-swiss.md:33-35 '(4) Der echte 429-Body — Nicht gemessen'
- Verified as true against code: FALLBACK_MAX_CALLS=8 (tools.py:790), cache TTLs 15/60/1440 min (client.py:263-265), cache-before-availability (client.py:836-843), 8 verified facets only (client.py:207-220), tzdata on win32 (pyproject.toml:41), tool-hash snapshot test (tests/test_server.py:23,89-91), SHA-pinned actions (ci.yml, publish.yml), docs/DEMO.md, docs/LICENSES.md, scripts/*.py present
- grep of intent vocabulary (not yet|noch nicht|planned|todo|coming soon...) over CHANGELOG/README/docs/src — no hits (negative control fired)

### Gemessen / Geschlossen / Offen

**Gemessen**
- CHANGELOG.md:78-79 — '[Unreleased] Added: Audit audits/AUDIT_2026-09-26.md ... and its run directory' — file absent; `git ls-files audits` returns 0 files at bd0e371 (audits/ is untracked)
- CHANGELOG.md:67-70 — 'recall floors ... for all eight tool paths' vs tests/test_live.py:127-247: floors for 6 tools (search, find_accommodation, find_tours, webcams_near, explore_area, find_events) + a client.search partner check; none for get_details or source_status
- README.md:232 — 'Unknown facet names are dropped silently' vs src/discover_swiss_mcp/client.py:210-214 and CHANGELOG.md:109-112/169-171 — an invented name answers HTTP 400; only filterPropertyName spellings are dropped
- src/discover_swiss_mcp/client.py:117-127 — comment 'Fifteen fields, every one of them answered live' vs probes/PROBE_OPEN_discover-swiss.md:16-27 — six of them verified on 3 of the 5 fallback endpoints
- src/discover_swiss_mcp/client.py:534-535 — docstring states the gateway's 429 wording as fact vs probes/PROBE_OPEN_discover-swiss.md:33-35 '(4) Der echte 429-Body — Nicht gemessen'
- Verified as true against code: FALLBACK_MAX_CALLS=8 (tools.py:790), cache TTLs 15/60/1440 min (client.py:263-265), cache-before-availability (client.py:836-843), 8 verified facets only (client.py:207-220), tzdata on win32 (pyproject.toml:41), tool-hash snapshot test (tests/test_server.py:23,89-91), SHA-pinned actions (ci.yml, publish.yml), docs/DEMO.md, docs/LICENSES.md, scripts/*.py present
- grep of intent vocabulary (not yet|noch nicht|planned|todo|coming soon...) over CHANGELOG/README/docs/src — no hits (negative control fired)

**Geschlossen**
- Mode 1 done claim by claim for [Unreleased] and README Known limitations. No stale 'pending' sentences, but four statements claim more than the repo holds. Note: the caller asked for CHANGELOG-vs-code under DRIFT-008; in the catalogue that is DRIFT-006, so it is judged here.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein CHANGELOG ist kein Beiwerk, sondern eine Reihe von Behauptungen über den Code. Der Abschnitt `[Unreleased]` ist dabei die einzige Stelle im Repository, die in die **Zukunft** zeigt: Wer ihn liest — die Maintainerin nach zwei Wochen, die Auditorin beim Einstieg, die Nutzerin vor dem Upgrade —, liest ihn als Plan. Was dort steht, gilt als noch nicht getan.

### Remediation

Remove or reword the audit bullet until the report is committed; change 'all eight tool paths' to the six tools actually covered; rewrite README #8 ('filterPropertyName spellings are dropped silently, invented names answer 400; only verified names are sent'); qualify the two client.py comments with what was measured.

**Disposition:** CHANGELOG claimed an audit report not yet in the repo (now added), said the canaries cover all eight tool paths (six do; get_details and source_status are covered by the fidelity canary and not at all), and README limitation 8 said unknown facet names are always dropped silently (an invented name answers 400). Corrected after the audit.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DRIFT-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
