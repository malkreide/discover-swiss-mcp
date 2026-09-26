## Finding: OPS-001 — Test-Strategie: Unit-Tests mocked + Live-Tests gemarkert

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-001` |
| **PDF-Reference** | Anhang C1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No live test for source_status (grep over tests/test_live.py: no source_status)
- No separate nightly or manual live-test workflow: .github/workflows contains only ci.yml and publish.yml
- No test-specific credential: live suite reads DISCOVER_SWISS_KEY from the environment (test_live.py:84-90); no LIVE_TEST secret
- No live workflow, hence no timeout-minutes bound for it
- Live suite builds a fresh DiscoverSwissClient per test (function-scoped fixture tests/test_live.py:99-104): cache unused, retry ladder repeated per test on outage
- Live suite uses production timeouts (REQUEST_TIMEOUT 20 s, TOTAL_BUDGET 25 s, client.py:235,248); no tighter test values

### Expected Behavior

- [ ] `tests/test_unit.py` mit mindestens 5 Unit-Tests pro Tool
- [ ] `tests/test_live.py` mit mindestens 1 Live-Test pro Tool
- [ ] Unit-Tests verwenden `respx` (Python) oder `nock` (Node) für HTTP-Mocking
- [ ] Live-Tests sind mit `@pytest.mark.live` (oder Äquivalent) markiert
- [ ] Marker im `pyproject.toml` registriert
- [ ] CI-Workflow läuft `pytest -m "not live"`
- [ ] Separater nightly/manueller Live-Test-Workflow
- [ ] Live-Tests nutzen Test-spezifische Credentials, nicht Production-Keys (Synergie zu SEC-013)
- [ ] Der Live-Workflow hat `timeout-minutes` — eine Obergrenze, die den Normalfall nicht schneidet
- [ ] Die Live-Suite teilt Client und Cache, statt pro Test neu zu laden; der Pool wird beim Teardown geschlossen
- [ ] Test-Timeouts sind enger gesetzt als die Prod-Defaults: eine tote Quelle meldet sich in Minuten, nicht in einer Viertelstunde

### Evidence

- tests/conftest.py:24, 87-96 — respx router bound to the pinned base URL for all unit tests
- tests/test_live.py:60 — pytestmark = pytest.mark.live
- pyproject.toml:72-75 — 'live' marker registered
- .github/workflows/ci.yml:66-67 — pytest -m "not live"
- runtime: pytest -m 'not live' -> 215 passed, 18 deselected; unit call sites per tool >= 5 (search 21, get_details 9, find_accommodation 6, find_tours 8, find_events 9, webcams_near 5 tests, explore_area 8, source_status 7)
- tests/test_live.py:135-323 — 18 live canaries covering 7 of 8 tools

### Gemessen / Geschlossen / Offen

**Gemessen**
- tests/conftest.py:24, 87-96 — respx router bound to the pinned base URL for all unit tests
- tests/test_live.py:60 — pytestmark = pytest.mark.live
- pyproject.toml:72-75 — 'live' marker registered
- .github/workflows/ci.yml:66-67 — pytest -m "not live"
- runtime: pytest -m 'not live' -> 215 passed, 18 deselected; unit call sites per tool >= 5 (search 21, get_details 9, find_accommodation 6, find_tours 8, find_events 9, webcams_near 5 tests, explore_area 8, source_status 7)
- tests/test_live.py:135-323 — 18 live canaries covering 7 of 8 tools

**Geschlossen**
- 5 of 11 criteria met (< half). Unit side is solid (respx, marker, CI exclusion); the live side exists but runs only manually, with per-test clients and production timeouts, and misses one tool.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Aus dem Sormena-Pattern bewährt: zwei Test-Kategorien mit klarer Trennung.

### Remediation

Add .github/workflows/live.yml (schedule + workflow_dispatch, timeout-minutes: 10, secret LIVE_TEST_DISCOVER_SWISS_KEY), make the live client session-scoped (pytest_asyncio fixture scope/loop_scope='session') with tighter timeouts, and add a source_status canary.

**Disposition:** Add a source_status live canary and give the live module one shared client and a test timeout.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-001` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
