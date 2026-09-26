## Finding: DRIFT-008 — Ein Live-Test muss die Quelle erreichen — «markiert» ist nicht «live»

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-008` |
| **PDF-Reference** | Custom (Portfolio-Fundstück zh-education-mcp, 2026-08-08) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No suite-wide guard hook that fails a live test whose resolver/env is stubbed; protection rests on per-module override by fixture name
- Stubbing fixtures do not self-exempt via `if 'live' in request.keywords`; a live test added in any other module would run against 203.0.113.10 with key 'test-key'
- No reference value captured at import and no counter-probe
- Live tests have never run, so reaching the source is not demonstrated

### Expected Behavior

- [ ] Jede `autouse`-Fixture, die Auflösung, Transport, Zeit oder Umgebung ersetzt, nimmt Live-Tests aus — oder in ihrem Geltungsbereich existiert nachweislich kein Live-Test
- [ ] Ein Wächter bricht Live-Tests ab, deren Aussenwelt ersetzt wurde, und zwar **suiteweit**, nicht je Datei
- [ ] Der Wächter läuft zwischen Fixture-Aufbau und Testkörper (Hook), nicht als Fixture
- [ ] Der echte Referenzwert wird beim Import festgehalten, vor jeder Fixture
- [ ] Die Gegenprobe ist geführt und in beide Richtungen belegt: Rückfall fällt, ehrlicher Live-Test bleibt grün
- [ ] Die Fehlermeldung nennt die Behebung, nicht nur den Zustand — wer sie liest, sucht sonst zuerst bei der Quelle

### Evidence

- tests/conftest.py:41-72 — three autouse fixtures: api_key (setenv test-key), _clean_env, _pin_dns (patches net._resolve to 203.0.113.10)
- tests/test_live.py:84-96 — live module overrides api_key and _pin_dns by name
- pytest --fixtures-per-test (run in this audit): all 18 live tests use _pin_dns from tests/test_live.py:94 and api_key from tests/test_live.py:85; negative control: tests/test_client.py uses _pin_dns from tests/conftest.py:66 (34 tests)
- src/discover_swiss_mcp/client.py:275-279 — waits go through client._sleep, not a patched stdlib function
- grep request.keywords|pytest_runtest_call|item.keywords|getaddrinfo|_REAL_ in tests/ — no hit (negative control: pattern fires on 'if "live" in request.keywords:')

### Gemessen / Geschlossen / Offen

**Gemessen**
- tests/conftest.py:41-72 — three autouse fixtures: api_key (setenv test-key), _clean_env, _pin_dns (patches net._resolve to 203.0.113.10)
- tests/test_live.py:84-96 — live module overrides api_key and _pin_dns by name
- pytest --fixtures-per-test (run in this audit): all 18 live tests use _pin_dns from tests/test_live.py:94 and api_key from tests/test_live.py:85; negative control: tests/test_client.py uses _pin_dns from tests/conftest.py:66 (34 tests)
- src/discover_swiss_mcp/client.py:275-279 — waits go through client._sleep, not a patched stdlib function
- grep request.keywords|pytest_runtest_call|item.keywords|getaddrinfo|_REAL_ in tests/ — no hit (negative control: pattern fires on 'if "live" in request.keywords:')

**Geschlossen**
- The concrete trap of the Belegfall is avoided today (fixtures overridden, verified with --fixtures-per-test), and the DNS stub is on an own seam (net._resolve) rather than socket. Only 1 of the applicable criteria is met; guard, hook, reference value and counter-probe are absent. Advisory check. (Caller's note 'CHANGELOG against code' belongs to DRIFT-006 in the catalogue and is judged there.)

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Live-Test ist im Katalog kein gewöhnlicher Test. Er ist der **Beleg**: die einzige Stelle, an der eine Annahme über eine fremde Quelle widerlegt werden kann. Jeder andere Test prüft gegen eine Fixture, und die Fixture ist aus derselben Annahme geschrieben wie der Code — sie bestätigt sie, so lange es sie gibt. Deshalb verlangt [`SKILL.md` §2.6](../SKILL.md), dass ein Live-Test, der **nicht gelaufen** ist, `todo` ergibt und nicht `pass`.

### Remediation

Add `if 'live' in request.keywords: return` to api_key and _pin_dns in conftest.py; add a pytest_runtest_call hook in conftest.py that fails a live test when net._resolve is not the original captured at import or DISCOVER_SWISS_KEY == 'test-key'; add a counter-probe test file.

**Disposition:** Add a suite-wide guard: a conftest hook that fails a live-marked test if the documentation IP pin or test-key is active.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DRIFT-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
