# MCP-Server Audit-Report — `discover-swiss-mcp`

**Audit-Datum:** 2026-09-26
**Skill-Version:** 2.3.0
**Catalog-Version:** 2bbded9079fd

---

## 1. Executive Summary

Server `discover-swiss-mcp` wurde gegen 85 anwendbare Best-Practice-Checks geprüft. 25 bestanden, 56 Findings dokumentiert (5 critical, 27 high, 23 medium, 1 low). Production-Readiness: NICHT erreicht — blockierend: DRIFT-004, OPS-001, OPS-003, SEC-003, SEC-007, SEC-021, SEC-024, SEC-028. Zusätzlich 3 advisory-Finding(s) auf blockierender Severity: DRIFT-008, FID-006, OPS-010. 4 Check(s) konnten nicht verifiziert werden und zählen weder als bestanden noch als fehlgeschlagen: IDENT-001, IDENT-007, OPS-004, SEC-026. Sie gehören unter «Offen».

**Production-Readiness:** NO (über 4 nicht verifizierte Checks)

---

## 2. Profil-Snapshot

| Feld | Wert |
|---|---|
| Server-Name | `discover-swiss-mcp` |
| Audit-Datum | 2026-09-26 |
| Skill-Version | 2.3.0 |
| Catalog-Version | 2bbded9079fd |
| transport | `dual` |
| auth_model | `API-Key` |
| data_class | `Public Open Data` |
| write_capable | `False` |
| deployment | `['local-stdio']` |
| uses_sampling | `False` |
| tools_make_external_requests | `True` |
| stadt_zuerich_context | `False` |
| schulamt_context | `False` |
| data_source.is_swiss_open_data | `True` |

---

## 3. Applicability

### Status pro Kategorie

| Kategorie | Pass | Fail | Partial | Not verified | Todo | N/A |
|---|---|---|---|---|---|---|
| ARCH | 7 | 4 | 10 | 0 | 0 | 0 |
| CH | 1 | 0 | 0 | 0 | 0 | 0 |
| DEP | 0 | 0 | 1 | 0 | 0 | 0 |
| DRIFT | 2 | 3 | 2 | 0 | 0 | 0 |
| FID | 0 | 2 | 5 | 0 | 0 | 0 |
| HITL | 1 | 0 | 0 | 0 | 0 | 0 |
| IDENT | 1 | 0 | 4 | 2 | 0 | 0 |
| OBS | 2 | 0 | 4 | 0 | 0 | 0 |
| OPS | 1 | 4 | 4 | 1 | 0 | 0 |
| SCALE | 2 | 0 | 1 | 0 | 0 | 0 |
| SDK | 3 | 0 | 1 | 0 | 0 | 0 |
| SEC | 5 | 5 | 6 | 1 | 0 | 0 |
| **Total** | **25** | **18** | **38** | **4** | **0** | **0** |

---

## 4. Findings-Übersicht

_Policy: `fail-or-partial`_

| ID | Category | Severity | Status |
|---|---|---|---|
| ARCH-005 | ARCH | critical | partial |
| FID-001 | FID | critical | partial |
| SEC-002 | SEC | critical | partial |
| SEC-004 | SEC | critical | partial |
| SEC-016 | SEC | critical | partial |
| ARCH-013 | ARCH | high | partial |
| ARCH-014 | ARCH | high | partial |
| ARCH-015 | ARCH | high | partial |
| ARCH-016 | ARCH | high | partial |
| DEP-001 | DEP | high | partial |
| DRIFT-002 | DRIFT | high | partial |
| DRIFT-004 | DRIFT | high | fail |
| DRIFT-008 | DRIFT | high | fail |
| FID-002 | FID | high | partial |
| FID-003 | FID | high | partial |
| FID-006 | FID | high | fail |
| FID-007 | FID | high | partial |
| IDENT-006 | IDENT | high | partial |
| OBS-001 | OBS | high | partial |
| OPS-001 | OPS | high | fail |
| OPS-003 | OPS | high | fail |
| OPS-005 | OPS | high | partial |
| OPS-009 | OPS | high | partial |
| OPS-010 | OPS | high | fail |
| SEC-003 | SEC | high | fail |
| SEC-006 | SEC | high | partial |
| SEC-007 | SEC | high | fail |
| SEC-013 | SEC | high | partial |
| SEC-018 | SEC | high | partial |
| SEC-021 | SEC | high | fail |
| SEC-024 | SEC | high | fail |
| SEC-028 | SEC | high | fail |
| ARCH-002 | ARCH | medium | partial |
| ARCH-003 | ARCH | medium | fail |
| ARCH-008 | ARCH | medium | fail |
| ARCH-011 | ARCH | medium | partial |
| ARCH-012 | ARCH | medium | fail |
| ARCH-018 | ARCH | medium | partial |
| ARCH-020 | ARCH | medium | fail |
| ARCH-021 | ARCH | medium | partial |
| ARCH-022 | ARCH | medium | partial |
| DRIFT-005 | DRIFT | medium | fail |
| DRIFT-006 | DRIFT | medium | partial |
| FID-004 | FID | medium | partial |
| FID-005 | FID | medium | fail |
| IDENT-002 | IDENT | medium | partial |
| IDENT-003 | IDENT | medium | partial |
| OBS-003 | OBS | medium | partial |
| OBS-007 | OBS | medium | partial |
| OBS-008 | OBS | medium | partial |
| OPS-002 | OPS | medium | partial |
| OPS-007 | OPS | medium | partial |
| OPS-008 | OPS | medium | fail |
| SCALE-010 | SCALE | medium | partial |
| SDK-003 | SDK | medium | partial |
| IDENT-004 | IDENT | low | partial |

**Gesamt:** 56 Findings

---

## 5. Detail-Findings

### ARCH-002

## Finding: ARCH-002 — Tool-Beschreibung mit Use-Case-Tags

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-002` |
| **PDF-Reference** | Sec 2.2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No structured use-case marker (<use_case> or equivalent section) in any tool; explicit 'when to use' statements exist for only ~3 of 8 tools (explore_area, source_status, find_events) — below the 80% criterion
- search vs find_accommodation (both can return hotels) are not explicitly differentiated in either description

### Expected Behavior

- [ ] Tool-Beschreibungen sind ≥ 100 Zeichen im Median
- [ ] Use-Case-Tag (`<use_case>` oder Äquivalent) in mindestens 80% der Tools vorhanden
- [ ] Wo relevant: Important-Notes-Tag mit Caveats / Limitierungen
- [ ] Bei mehreren ähnlichen Tools: Description macht Differenzierung explizit

### Evidence

- runtime (mcp.list_tools, whitespace-normalised): description lengths search 1531, get_details 819, find_accommodation 991, find_tours 1346, find_events 1160, webcams_near 666, explore_area 1042, source_status 573 — median 1016.5, min 573
- src/discover_swiss_mcp/server.py:262 — find_accommodation carries caveats ('NO availability and NO nightly prices — never state that a room is free')
- src/discover_swiss_mcp/server.py:292 — find_events: 'Treat this tool as a supplement: if it returns nothing, name a regional event calendar'
- src/discover_swiss_mcp/server.py:322 and :337 — explore_area / source_status carry explicit when-to-use sentences
- grep '<use_case>|<important_notes>|<example>' src/ → 0 hits (negative control: same pattern hits ARCH-002.md:19-20)

### Gemessen / Geschlossen / Offen

**Gemessen**
- runtime (mcp.list_tools, whitespace-normalised): description lengths search 1531, get_details 819, find_accommodation 991, find_tours 1346, find_events 1160, webcams_near 666, explore_area 1042, source_status 573 — median 1016.5, min 573
- src/discover_swiss_mcp/server.py:262 — find_accommodation carries caveats ('NO availability and NO nightly prices — never state that a room is free')
- src/discover_swiss_mcp/server.py:292 — find_events: 'Treat this tool as a supplement: if it returns nothing, name a regional event calendar'
- src/discover_swiss_mcp/server.py:322 and :337 — explore_area / source_status carry explicit when-to-use sentences
- grep '<use_case>|<important_notes>|<example>' src/ → 0 hits (negative control: same pattern hits ARCH-002.md:19-20)

**Geschlossen**
- Length and caveats are strong (median ~1000 chars, many limitations stated). The use-case-tag criterion (≥80% of tools) and the differentiation of overlapping tools are not met.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: LLMs wählen Tools nicht über exakte Namens-Treffer, sondern über semantische Embeddings der Tool-Beschreibung. Eine Beschreibung wie `"Searches database"` lässt das Modell zwischen drei `getX`-Tools rätseln. Eine Beschreibung mit explizitem Use-Case-Tag, Trigger-Phrasen und Negativ-Hinweisen («NICHT verwenden für…») reduziert Halluzinationen drastisch.

### Remediation

Add a short, uniformly placed use-case lead (e.g. 'Use when …' / 'Not for …') to each description, and state in search/find_accommodation which one to prefer for lodging questions; regenerate docs/tool-hashes.json.

**Disposition:** Add a 'when to use / not to use' line to the five tools that lack one; separate search from find_accommodation explicitly.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-003

## Finding: ARCH-003 — «Not Found» Anti-Pattern: Heuristiken statt leerer Antworten

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-003` |
| **PDF-Reference** | Sec 2.2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No match_type (exact/fuzzy/none) field in any response
- No suggestions derived from the caller's own term; the hint is generic advice
- The empty response does not state that the server did not broaden the query (searched once, unchanged term)
- Mode-3 test pair missing: no respx test asserting route.call_count == 1 and unchanged searchText on an empty result, and no suggestion-half test; no Gegenprobe

### Expected Behavior

- [ ] Bei nicht-sensiblen Such-Tools: leere Ergebnisse triggern Fuzzy-Match oder Suggestion-Mechanismus
- [ ] Response enthält `match_type`-Feld oder ähnlich (exact / fuzzy / none)
- [ ] Bei `match_type == "none"`: ein actionable Hinweis (Vorschläge, andere Tools, Term-Verfeinerung)
- [ ] Bei sensiblen Tools: ausschliesslich exakte Lookups, kein Fuzzy-Fallback (dokumentiert)
- [ ] Pro Tool-Aufruf geht **genau ein** Upstream-Request raus, und sein Suchbegriff ist der des Aufrufers, **unverändert** — erhoben am Zähler der Route (Modus 3), nicht am Rückgabewert
- [ ] Vorschläge sind aus der Eingabe **abgeleitet** (Kürzung, Präfix), nicht aus einem Korpus-Vokabular geholt — letzteres ist eine zweite Abfrage in anderer Verpackung, mit eigenem Recall-Risiko
- [ ] Vorschläge unterhalb weniger Zeichen werden verworfen — ein Präfix, das den halben Bestand matcht, ist kein nächster Schritt («AG» ist kein Suchbegriff)
- [ ] Heuristische Treffer stehen in einem **eigenen** Feld, zusammen mit dem Begriff, der sie erzeugt hat — nie in derselben Liste wie die exakten
- [ ] Die Antwort **sagt**, dass nicht verbreitert wurde; ohne diesen Satz schliesst das Modell aus dem Schweigen, es sei schon alles versucht
- [ ] Das Testpaar aus Modus 3 ist **vollständig** vorhanden — eine Hälfte belegt, dass Vorschläge erscheinen, die andere, dass keiner davon abgefragt wurde
- [ ] **Gegenprobe:** Der Zähler ist einmal gegen eine Fassung gelaufen, die ihre Vorschläge selbst absucht, und hat dort angeschlagen. Ein Modus, der nur am korrigierten Server grün wird, prüft die Fixture

### Evidence

- src/discover_swiss_mcp/tools.py:171-177 — SEARCH_EMPTY_HINT: actionable next steps (match='all', drop types, near instead of locality, call explore_area)
- src/discover_swiss_mcp/tools.py:664-694 — _paged_hint distinguishes nothing-matched / past-the-end / all-withheld
- tests/test_tools.py:273-281 — empty search asserts hint == SEARCH_EMPTY_HINT (return value only, no route counter)
- src/discover_swiss_mcp/models.py:33-53 — Envelope has no match_type field; grep 'match_type|suggest' src/discover_swiss_mcp/tools.py → only a docstring hit at :670

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:171-177 — SEARCH_EMPTY_HINT: actionable next steps (match='all', drop types, near instead of locality, call explore_area)
- src/discover_swiss_mcp/tools.py:664-694 — _paged_hint distinguishes nothing-matched / past-the-end / all-withheld
- tests/test_tools.py:273-281 — empty search asserts hint == SEARCH_EMPTY_HINT (return value only, no route counter)
- src/discover_swiss_mcp/models.py:33-53 — Envelope has no match_type field; grep 'match_type|suggest' src/discover_swiss_mcp/tools.py → only a docstring hit at :670

**Geschlossen**
- Empty results are never bare — the hint is actionable and names other tools, which covers criteria 1 and 3. But of the applicable criteria (1,2,3,5,6,9,10,11; 4,7,8 n/a for public data without fuzzy arm) only two are met; per the check a server without the counter test pair has not shown the property.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: LLMs reagieren empirisch nachweisbar empfindlich auf negativ-framing in Tool-Responses. Eine Antwort wie `"No results found"` oder `[]` ohne Kontext führt häufig zu einer von zwei Failure-Modes:

### Remediation

Add match_type ('exact'|'none') to the paged envelope; on returned==0 add a sentence 'searched once with your term, not broadened'; add term-derived suggestions (shorter variants ≥4 chars) in a separate field; add the two respx tests (suggestions appear; route.call_count==1 with unchanged searchText) and run the counter once against a mutated version that searches its suggestions.

**Disposition:** Empty results already carry a concrete hint; a match_type field and term-based suggestions need upstream support that /search does not offer (no fuzzy flag). Revisit with FID-005.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-005

## Finding: ARCH-005 — Keine Hardcoded Secrets: Env-Vars / Secret Manager only

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-005` |
| **PDF-Reference** | Sec 2.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- .env.example with placeholders does not exist (and .gitignore:16 '.env.*' would also ignore it — no '!.env.example' exception)
- No gitleaks/trufflehog (or equivalent) secret-scan step in .github/workflows/ci.yml or publish.yml
- Settings are hand-rolled from os.environ rather than pydantic-settings (accepted as 'o.ä.', noted only)

### Expected Behavior

- [ ] Keine API-Keys, Passwörter, Tokens, Connection-Strings im Source-Code
- [ ] Keine Default-Werte mit echten Secrets in `os.environ.get(..., default=...)` oder ähnlich
- [ ] Secrets werden zur Startzeit aus Env-Vars / Secret-Manager geladen (Pydantic-Settings o.ä.)
- [ ] In-Memory-Repräsentation als `SecretStr` (Python) oder gleichwertig (kein `str`)
- [ ] Secrets erscheinen **nicht** in Log-Outputs (keine `f"{settings}"`-Logs)
- [ ] `.gitignore` enthält `.env`, `.env.*` (ausser `.env.example`)
- [ ] `.env.example` mit Platzhaltern existiert und ist im Repo
- [ ] CI-Workflow mit Gitleaks oder Trufflehog läuft auf PRs

### Evidence

- src/discover_swiss_mcp/config.py:45,91,125 — api_key is SecretStr read from DISCOVER_SWISS_KEY with empty default (no real key as fallback)
- src/discover_swiss_mcp/config.py:58-76 and server.py:129-134 — only safe_summary() is logged ('api_key': 'set'|'missing'); runtime startup log line shows "api_key": "set"
- .gitignore:15-16 — .env and .env.* ignored
- grep secret pattern (api_key|password|secret|token = '16+ chars') over src/ → 0 hits (negative control: fires on a scratch file with api_key = "abcdefghijklmnopqrstuvwx"); AKIA/connection-string patterns → 0 hits; git grep over tracked files shows the key only as env reads in probes/*.py (e.g. probes/probe_detail.py:28)
- attempted gitleaks/trufflehog: neither installed in this environment (which → not found); history grep for 32-hex subscription-key values → no hits

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:45,91,125 — api_key is SecretStr read from DISCOVER_SWISS_KEY with empty default (no real key as fallback)
- src/discover_swiss_mcp/config.py:58-76 and server.py:129-134 — only safe_summary() is logged ('api_key': 'set'|'missing'); runtime startup log line shows "api_key": "set"
- .gitignore:15-16 — .env and .env.* ignored
- grep secret pattern (api_key|password|secret|token = '16+ chars') over src/ → 0 hits (negative control: fires on a scratch file with api_key = "abcdefghijklmnopqrstuvwx"); AKIA/connection-string patterns → 0 hits; git grep over tracked files shows the key only as env reads in probes/*.py (e.g. probes/probe_detail.py:28)
- attempted gitleaks/trufflehog: neither installed in this environment (which → not found); history grep for 32-hex subscription-key values → no hits

**Geschlossen**
- No secret in code or history found; key handling (SecretStr, masked summary, env only) is exemplary. Two of eight criteria (.env.example, CI secret scan) are unmet, so not a pass on a critical check; no leak evidence, gitleaks not runnable here.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Hardcoded Secrets (API-Keys, Passwörter, Tokens, Connection-Strings, Encryption-Keys) im Source-Code sind die häufigste vermeidbare Sicherheitsschwäche in MCP-Server-Repositories. Sobald das Repo öffentlich ist (oder versehentlich öffentlich wird), oder ein Mitarbeiter aus dem Team ausscheidet, sind alle Secrets kompromittiert.

### Remediation

Add .env.example with DISCOVER_SWISS_KEY=replace-with-your-key and '!.env.example' in .gitignore; add a gitleaks-action job (SHA-pinned) on push/pull_request.

**Disposition:** Add .env.example with placeholders and a '!.env.example' exception in .gitignore; add a secret scan step to CI.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-008

## Finding: ARCH-008 — Drei Primitive nutzen: Tools, Resources und Prompts

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-008` |
| **PDF-Reference** | Anhang A2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Only one primitive (tools) and no README rationale for tools-only
- No documented review of read-only tools (get_details by identifier, source_status) as resource candidates
- Capabilities advertise prompts/resources (incl. resources.subscribe) that the server does not provide (SDK default)

### Expected Behavior

- [ ] Server nutzt mindestens zwei der drei Primitive (Tools + Resources oder Tools + Prompts), oder
- [ ] README dokumentiert begründet, warum nur Tools verwendet werden
- [ ] Bei Resources: URI-Schema ist konsistent und dokumentiert
- [ ] Bei Prompts: Template-Liste ist kuratiert, nicht beliebig
- [ ] Tools, die rein read-only sind (idempotent, side-effect-frei, deterministisch), werden auf Resources-Migrations-Potential geprüft

### Evidence

- grep '@mcp.resource|@mcp.prompt|.resource(|.prompt(' src/ → 0 hits (tools only)
- grep -iE 'resources|prompts|primitive' README.md README.de.md → 0 hits (negative control: same pattern hits ARCH-008.md:3)
- runtime: resources/list, prompts/list, resources/templates/list return empty lists, while server/discover advertises capabilities prompts{listChanged:true} and resources{listChanged:true, subscribe:true}

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep '@mcp.resource|@mcp.prompt|.resource(|.prompt(' src/ → 0 hits (tools only)
- grep -iE 'resources|prompts|primitive' README.md README.de.md → 0 hits (negative control: same pattern hits ARCH-008.md:3)
- runtime: resources/list, prompts/list, resources/templates/list return empty lists, while server/discover advertises capabilities prompts{listChanged:true} and resources{listChanged:true, subscribe:true}

**Geschlossen**
- Neither alternative of criterion 1/2 is met: no second primitive and no documented justification.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: MCP definiert drei orthogonale Primitive, von denen die meisten Server nur eines nutzen:

### Remediation

Add a 'MCP primitives' paragraph to README.md and README.de.md explaining tools-only (e.g. identifiers only come from searches; read-only tools are needed for provenance envelopes), or expose get_details as a resource template (discover-swiss://object/{identifier}); consider not advertising unused capabilities.

**Disposition:** Tools-only is deliberate (a tourist question is an action, not a resource); the README will say so in one sentence.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-011

## Finding: ARCH-011 — Standardisierte Repo-Struktur (src-Layout, tests, README.de.md)

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-011` |
| **PDF-Reference** | Anhang A8 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- >5 tools but no tools/ directory with file-per-group split; tools.py is 2384 lines and server.py 374 lines (>200)
- Deviation from the standard layout is not justified in README.md or README.de.md
- CI workflow is named ci.yml instead of test.yml (functionally equivalent; noted only)

### Expected Behavior

- [ ] Top-Level-Pflicht-Files vorhanden: `README.md`, `README.de.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`
- [ ] Verzeichnisse vorhanden: `src/`, `tests/`, `.github/workflows/`
- [ ] `src/`-Layout korrekt (kein flat package)
- [ ] CI-Workflows: mindestens `test.yml` (CI ohne live-Tests) und `publish.yml`
- [ ] `README.de.md` ist parallel zu `README.md` (gleiche Top-Level-Sektionen)
- [ ] Bei > 5 Tools: `tools/`-Verzeichnis mit File-pro-Gruppe-Aufteilung
- [ ] Abweichungen vom Standard sind in `README.md` **oder** `README.de.md` begründet — eine Begründung ausschliesslich in `SECURITY.md`, `CONTRIBUTING.md`, `docs/`, einem Issue oder einer Commit-Message zählt nicht

### Evidence

- top level: README.md, README.de.md, CHANGELOG.md, LICENSE, pyproject.toml all present; src/, tests/, .github/workflows/ (ci.yml, publish.yml) present
- pyproject.toml:66-67 — [tool.hatch.build.targets.wheel] packages = ['src/discover_swiss_mcp'] (src layout)
- .github/workflows/ci.yml:66-67 — pytest -m "not live"; .github/workflows/publish.yml present
- README.md vs README.de.md '^## ' headings: 20 each, same order, semantically matching (e.g. Anchor demo queries/Anker-Abfragen, Known limitations/Bekannte Einschränkungen)
- src/discover_swiss_mcp/tools.py (2384 lines) holds all eight *_impl; src/discover_swiss_mcp/server.py is 374 lines; no tools/ package
- README.md:254-274 — Project Structure lists tools.py but gives no reason for deviating from a tools/ package

### Gemessen / Geschlossen / Offen

**Gemessen**
- top level: README.md, README.de.md, CHANGELOG.md, LICENSE, pyproject.toml all present; src/, tests/, .github/workflows/ (ci.yml, publish.yml) present
- pyproject.toml:66-67 — [tool.hatch.build.targets.wheel] packages = ['src/discover_swiss_mcp'] (src layout)
- .github/workflows/ci.yml:66-67 — pytest -m "not live"; .github/workflows/publish.yml present
- README.md vs README.de.md '^## ' headings: 20 each, same order, semantically matching (e.g. Anchor demo queries/Anker-Abfragen, Known limitations/Bekannte Einschränkungen)
- src/discover_swiss_mcp/tools.py (2384 lines) holds all eight *_impl; src/discover_swiss_mcp/server.py is 374 lines; no tools/ package
- README.md:254-274 — Project Structure lists tools.py but gives no reason for deviating from a tools/ package

**Geschlossen**
- Files, directories, src layout, CI and bilingual parity are fine; the tool-module split and the README justification for the deviation are missing (5 of 7 criteria).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Aus dem Schweizer Public-Data-Portfolio bewährt sich ein konsistentes Repo-Layout. Das ist nicht nur Code-Schönheit — es ist Operational Discipline:

### Remediation

Either split tools.py into src/discover_swiss_mcp/tools/ (search.py, lodging.py, tours.py, events.py, webcams.py, area.py, status.py) or add a sentence in README.md and README.de.md 'Project Structure' explaining why a single tools.py was kept.

**Disposition:** Split tools.py (2'384 lines) into a tools/ package per tool group. Deferred: pure refactor with tool-hash snapshot as guard, no behaviour change, not a release blocker.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-011` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-012

## Finding: ARCH-012 — protocolVersion-Pinning + CHANGELOG + SDK-Update-Disziplin

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-012` |
| **PDF-Reference** | Anhang A9 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Pinned constant is decorative: the per-request check and -32022 come from the SDK's own list, not from MCP_PROTOCOL_VERSION; legacy handshake versions (2024-11-05..2025-11-25) are still accepted
- Code comment asserts a guard test that does not exist
- CHANGELOG does not name the spec version
- README has no 'MCP Protocol Version' section and no update/breaking-change policy
- No Dependabot/Renovate for pip (SDK updates are not proposed)

### Expected Behavior

- [ ] `protocolVersion` ist im Server-Code explizit gepinnt (kein «latest», kein Default)
- [ ] Auf `2026-07-28`: Die gepinnte Version wird **pro Request** gegen `io.modelcontextprotocol/protocolVersion` aus `_meta` geprüft — eine Konstante ohne diesen Vergleich zählt nicht
- [ ] Auf `2026-07-28`: Nichtübereinstimmung liefert `UnsupportedProtocolVersionError` (`-32022`), und `server/discover` nennt dieselbe Versionsliste (`ARCH-016`)
- [ ] `CHANGELOG.md` vorhanden, im Keep-a-Changelog-Format
- [ ] CHANGELOG-Einträge nennen explizit Spec-Version-Bumps
- [ ] README hat Sektion «MCP Protocol Version» mit aktuell unterstützter Version
- [ ] Update-Policy im README dokumentiert
- [ ] Dependabot oder Renovate aktiv für monatliche SDK-Update-PRs

### Evidence

- src/discover_swiss_mcp/server.py:73 — MCP_PROTOCOL_VERSION = "2026-07-28"; used only in the startup log (:131) and tests/test_server.py:152 (snapshot equality), never passed to MCPServer or compared with _meta
- src/discover_swiss_mcp/server.py:69-72 — comment claims 'a test holds the constant against the SDK's own LATEST_PROTOCOL_VERSION'; grep LATEST_PROTOCOL_VERSION tests/ scripts/ → 0 hits (negative control: hits .venv/.../mcp_types/version.py:50) — the test does not exist
- runtime (streamable-http): tools/list with _meta protocolVersion 2030-01-01 → error -32022 data.supported ['2026-07-28'] (SDK mcp_types/version.py:41 MODERN_PROTOCOL_VERSIONS); server/discover supportedVersions ['2026-07-28']
- runtime: legacy initialize with protocolVersion 2025-06-18 → 200, negotiated 2025-06-18 — the pinned constant does not constrain what the server speaks
- CHANGELOG.md:1-8 — Keep a Changelog header; CHANGELOG.md:63-64 says 'pinned protocol version' without naming it
- grep -iE 'breaking|spec.version|protocol.version|migration' README.md README.de.md → 0 hits (negative control: 27 hits in ARCH-012.md)
- .github/dependabot.yml — only package-ecosystem github-actions, no pip

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:73 — MCP_PROTOCOL_VERSION = "2026-07-28"; used only in the startup log (:131) and tests/test_server.py:152 (snapshot equality), never passed to MCPServer or compared with _meta
- src/discover_swiss_mcp/server.py:69-72 — comment claims 'a test holds the constant against the SDK's own LATEST_PROTOCOL_VERSION'; grep LATEST_PROTOCOL_VERSION tests/ scripts/ → 0 hits (negative control: hits .venv/.../mcp_types/version.py:50) — the test does not exist
- runtime (streamable-http): tools/list with _meta protocolVersion 2030-01-01 → error -32022 data.supported ['2026-07-28'] (SDK mcp_types/version.py:41 MODERN_PROTOCOL_VERSIONS); server/discover supportedVersions ['2026-07-28']
- runtime: legacy initialize with protocolVersion 2025-06-18 → 200, negotiated 2025-06-18 — the pinned constant does not constrain what the server speaks
- CHANGELOG.md:1-8 — Keep a Changelog header; CHANGELOG.md:63-64 says 'pinned protocol version' without naming it
- grep -iE 'breaking|spec.version|protocol.version|migration' README.md README.de.md → 0 hits (negative control: 27 hits in ARCH-012.md)
- .github/dependabot.yml — only package-ecosystem github-actions, no pip

**Geschlossen**
- Met: CHANGELOG format; -32022 and discover list consistent (via SDK). Not met: an enforced server-side pin, CHANGELOG spec references, README section, update policy, SDK update automation. Fewer than half.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die MCP-Spec hat in 21 Monaten fünf Major-Updates erlebt (2024-11, 2025-03, 2025-06, 2025-11, 2026-07). Das ist eine ungewöhnlich hohe Velocity für einen Industriestandard. Konkrete Folgen für Server-Maintainer:

### Remediation

Add the promised test (MCP_PROTOCOL_VERSION in mcp_types.MODERN_PROTOCOL_VERSIONS and == server/discover supportedVersions); decide whether legacy handshake eras should be served (stateless_http / legacy off) and document it; add README/README.de 'MCP Protocol Version' section with update policy; name '2026-07-28' in CHANGELOG; add a pip ecosystem to .github/dependabot.yml grouping mcp.

**Disposition:** The pinned protocol version is not enforced and the comment in server.py promises a test that does not exist. Add the test against the SDK's LATEST_PROTOCOL_VERSION and correct the comment.

### Effort Estimate

S

### Dependencies / Blockers

Zusammen mit ARCH-015 und ARCH-016 (Protokoll-Identität).

### Verification After Fix

- Re-Audit von `ARCH-012` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-013

## Finding: ARCH-013 — Alle Netz-Transportpfade identisch verdrahtet

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-013` |
| **PDF-Reference** | Sec 2.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No test exercises the seam main() → streamable_http_app(host=…) (grep tests/ for streamable_http_app/transport/main → none); no mutation Gegenprobe
- Host-allow-list protection is armed only when DISCOVER_SWISS_MCP_HOST is loopback; a non-loopback bind silently runs without transport_security (documented only as 'localhost only' default, README.md:142)

### Expected Behavior

- [ ] Alle Codepfade, die eine ASGI-App konstruieren oder servieren, sind aufgezählt — eigener Builder, `run()`-Pfad, SSE, Factory
- [ ] Die Deployment-Manifeste sind mitgelesen; ein dort verdrahteter Pfad (`--factory`, eigener `CMD`) zählt mit
- [ ] Die Sicherheitsverdrahtung ist auf **allen** identisch, nicht nur auf dem bedingten Zweig
- [ ] Kein Scharfschalten hängt an einer sachfremden Bedingung (Auth gesetzt, CORS gesetzt, Debug aus)
- [ ] Der **vollständige** Bind-Parametersatz reist mit — Host **und** Port, nicht nur der Host
- [ ] Eine `uvicorn --factory` liest den Bind selbst aus derselben Quelle wie `main()`
- [ ] Pro Pfad existiert ein Test, der die Verdrahtung an der Naht prüft, nicht nur im Builder
- [ ] Gegenprobe geführt: Verdrahtung aus je einem Pfad entfernt, jedes Mal scheitert mindestens ein Test

### Evidence

- Path enumeration (grep streamable_http_app|sse_app|http_app|mcp.run|uvicorn.run in src/): server.py:364-368 uvicorn.run(mcp.streamable_http_app(host=settings.host), host=settings.host, port=settings.port) and server.py:370 mcp.run() (stdio) — no SSE app, no factory
- Deployment manifests: no Dockerfile/railway.toml/render.yaml/Procfile/docker-compose; pyproject.toml:58-59 console script → discover_swiss_mcp.server:main (same main as __main__.py:8-10)
- .venv/.../mcp/server/lowlevel/server.py:741-747 — SDK enables DNS-rebinding protection with allowed_hosts 127.0.0.1:*, localhost:*, [::1]:* (port wildcard, so the port need not travel) when host is loopback
- runtime: POST /mcp with Host: evil.example.com → 421, with Host: 127.0.0.1:8768 → 200; GET /mcp → 400 (no server-initiated GET stream)

### Gemessen / Geschlossen / Offen

**Gemessen**
- Path enumeration (grep streamable_http_app|sse_app|http_app|mcp.run|uvicorn.run in src/): server.py:364-368 uvicorn.run(mcp.streamable_http_app(host=settings.host), host=settings.host, port=settings.port) and server.py:370 mcp.run() (stdio) — no SSE app, no factory
- Deployment manifests: no Dockerfile/railway.toml/render.yaml/Procfile/docker-compose; pyproject.toml:58-59 console script → discover_swiss_mcp.server:main (same main as __main__.py:8-10)
- .venv/.../mcp/server/lowlevel/server.py:741-747 — SDK enables DNS-rebinding protection with allowed_hosts 127.0.0.1:*, localhost:*, [::1]:* (port wildcard, so the port need not travel) when host is loopback
- runtime: POST /mcp with Host: evil.example.com → 421, with Host: 127.0.0.1:8768 → 200; GET /mcp → 400 (no server-initiated GET stream)

**Geschlossen**
- Only one network path exists and it carries the SDK host allow-list, verified at runtime. The per-path seam test and the counter-proof are missing, which blocks pass on a high check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Server, der über Netz erreichbar ist, konstruiert seine ASGI-App fast nie an genau einer Stelle. Typisch sind drei bis vier Wege, und sie entstehen nacheinander, ohne dass jemand sie als Menge betrachtet:

### Remediation

Add a test that calls main() with DISCOVER_SWISS_MCP_TRANSPORT=streamable-http (uvicorn.run monkeypatched) and asserts the app rejects Host: evil.example.com with 421; run it once with host= removed to see it fail; pass explicit transport_security for non-loopback hosts or refuse them.

**Disposition:** Add a test for the main() to streamable_http_app(host=...) seam.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-013` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-014

## Finding: ARCH-014 — Retry-Politik gegenüber der Quelle: begrenzt, gestreut, gehorsam

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-014` |
| **PDF-Reference** | Custom (Katalog-Lücke, aufgefallen bei swiss-efv-mcp#16) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No jitter: client.py:236-241 deliberately deterministic (rationale: single-process client behind token bucket) — criterion unmet
- Retry-After only on 429 and only as integer seconds; 503 Retry-After ignored, HTTP-date form not parsed (client.py:546-548)
- Budget not bounded below the client timeout on all paths: a 429 extends the deadline by up to 30 s (client.py:772) → up to ~55 s; bucket.acquire() (client.py:714, 409-420, up to ~60 s) runs before asyncio.timeout and outside the deadline
- No test binds the wall-clock budget (no real-time slow-response test)

### Expected Behavior

Die ersten neun Kriterien setzen voraus, dass überhaupt wiederholt wird. Tut der Server das nicht, greift stattdessen der Abschnitt «Was gilt, wenn gar nicht wiederholt wird» — dann sind nur die drei dort genannten Bedingungen zu prüfen, und die letzten drei Kriterien dieser Liste.

- [ ] **Vorfrage:** Ob wiederholt wird, ist **festgestellt** — eigene Schleife, Bibliotheks-Dekorator **und** Transport-Ebene sind gelesen, nicht nur gegrept
- [ ] Wiederholt wird nur bei 5xx, 429, Timeout und Verbindungsfehler — **4xx ausser 429 bricht sofort ab**
- [ ] Der Backoff ist **gestreut** (Jitter), nicht rein deterministisch
- [ ] Wiederholt wird auch bei **Netzwerkfehlern und Timeouts**, nicht nur bei Status-Codes
- [ ] `Retry-After` bei 429/503 wird gelesen und **schlägt** die eigene Kurve, gedeckelt gegen unbrauchbar grosse Werte
- [ ] Der Deckel greift **nach** dem Jittern — nachgerechnet, nicht am Namen der Konstante abgelesen
- [ ] Es gibt ein **Gesamtbudget in Sekunden**, nicht nur eine Anzahl Versuche
- [ ] Das Budget hängt an einer **Wanduhr-Deadline**, nicht am Per-Operation-Timeout der HTTP-Bibliothek
- [ ] Das Budget liegt **unter dem Timeout des aufrufenden MCP-Clients** — sonst arbeitet der Server für niemanden
- [ ] Wiederholt wird auf **genau einer Ebene**; Transport-Retries der HTTP-Bibliothek stehen nachweislich auf null. **Das gilt auch für einen Server ohne eigene Schleife** — gesetzte Transport-Retries sind dort keine fehlende Politik, sondern eine ungeschriebene
- [ ] Schreibende Tools wiederholen nur mit Idempotency-Key (`ARCH-010`)
- [ ] Nach Erschöpfung: Fehler oder **gekennzeichnet** veralteter Cache — kein stilles Ausliefern alter Zahlen (`FID-003`)
- [ ] Die Werte sind im Test gebunden, nicht nur im Kommentar behauptet

### Evidence

- src/discover_swiss_mcp/client.py:707-807 — single retry loop in _call (hand-read); httpx.AsyncClient at :648 without transport= (retries 0); grep HTTPTransport|max_retries|Retry( src/ → 0 (negative control: hits .venv/.../httpx/_client.py:731)
- client.py:805-807 + tests/test_client.py:298-305 — other 4xx raise UpstreamRejectedError immediately, 1 call, no sleep
- client.py:731-747 + tests/test_client.py:258-262 — httpx.RequestError (network, timeouts) retried on the same ladder
- client.py:241 + tests/test_client.py:239-246 — fixed ladder 2/4/8 s, asserted exactly
- client.py:531-549,762-774 + tests/test_client.py:272-295 — 429 wait read from body ('Try again in N seconds') then Retry-After header, one retry, >30 s (RATE_LIMIT_MAX_WAIT :257) fails immediately
- client.py:248,703,716 — TOTAL_BUDGET 25 s as wall-clock deadline enforced with asyncio.timeout(remaining)
- client.py:776-781 — 403 quota is a state, never retried; exhaustion raises UpstreamUnavailableError mapped to degraded envelope (tools.py:697-705)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:707-807 — single retry loop in _call (hand-read); httpx.AsyncClient at :648 without transport= (retries 0); grep HTTPTransport|max_retries|Retry( src/ → 0 (negative control: hits .venv/.../httpx/_client.py:731)
- client.py:805-807 + tests/test_client.py:298-305 — other 4xx raise UpstreamRejectedError immediately, 1 call, no sleep
- client.py:731-747 + tests/test_client.py:258-262 — httpx.RequestError (network, timeouts) retried on the same ladder
- client.py:241 + tests/test_client.py:239-246 — fixed ladder 2/4/8 s, asserted exactly
- client.py:531-549,762-774 + tests/test_client.py:272-295 — 429 wait read from body ('Try again in N seconds') then Retry-After header, one retry, >30 s (RATE_LIMIT_MAX_WAIT :257) fails immediately
- client.py:248,703,716 — TOTAL_BUDGET 25 s as wall-clock deadline enforced with asyncio.timeout(remaining)
- client.py:776-781 — 403 quota is a state, never retried; exhaustion raises UpstreamUnavailableError mapped to degraded envelope (tools.py:697-705)

**Geschlossen**
- Retry exists and is well-scoped (what is retried, one layer, wall-clock deadline, 4xx abort). Jitter, full Retry-After handling and a hard total bound under the 30 s client timeout are missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Fast jeder Server im Portfolio wiederholt fehlgeschlagene Requests, und bis auf `OBS-007` («wie lautet die Meldung, wenn alle Versuche verbraucht sind») stellte der Katalog dazu keine Frage. Nicht *ob* wiederholt wird — das ist richtig —, sondern **was**, **wie schnell** und **wie lange**. Alle drei Antworten sind falsch, wenn niemand sie trifft: Die Voreinstellung ist «alles, sofort, unbegrenzt».

### Remediation

Add jitter after capping order (delay = min(base*2**n*(0.5+random()), MAX)); parse Retry-After on 503 and HTTP-date; move bucket.acquire inside the deadline or count it; cap deadline extension so total stays < 30 s; add a real-time test with a slow respx side effect and total_budget small.

**Disposition:** The 25 s budget can reach about 55 s after a 429 and rate-limiter waits are outside it; count both into the budget. Jitter stays off by design (single process behind a token bucket) and the reason is written next to RETRY_DELAYS.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-014` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-015

## Finding: ARCH-015 — Stateless-Konformität: kein initialize-Handshake, keine Server-Sitzung

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-015` |
| **PDF-Reference** | SEP-2575, SEP-2567 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- SDK serves the legacy era: POST initialize with protocolVersion 2025-06-18 over HTTP returns 200 and sets an mcp-session-id header — the server still issues session ids although it pins 2026-07-28 (streamable_http_app called without stateless_http, server.py:365)
- No order-independence test and no Gegenprobe against a stateful variant

### Expected Behavior

- [ ] Kein `initialize`- / `initialized`-Handler im eigenen Code
- [ ] Kein `Mcp-Session-Id` gelesen, gesetzt oder geroutet
- [ ] Protokollversion und Client-Capabilities werden **pro Request** aus `_meta` gelesen, nicht aus gespeichertem Verhandlungsergebnis
- [ ] Bei nicht unterstützter Version antwortet der Server mit `UnsupportedProtocolVersionError` (`-32022`), nicht mit einem generischen Fehler
- [ ] Keine prozesslokale Struktur trägt Aufrufer-bezogenen Zustand über Requests hinweg — geprüft am Code, nicht nur am Namen
- [ ] Die List-Antworten variieren nicht pro Verbindung
- [ ] **Gegenprobe:** Der Reihenfolge-Test ist einmal gegen eine absichtlich zustandsbehaftete Fassung gelaufen und hat dort angeschlagen. Ein Test, der nur die grüne Richtung kennt, belegt nichts

### Evidence

- grep 'initialize|notifications/initialized|InitializeResult|InitializationOptions' src/ → 0; grep 'mcp-session-id|session_manager|SessionManager|sessionId' src/ → 0 (negative controls: 10 and 9 hits in .venv/.../mcp/server/lowlevel/server.py)
- runtime: request with _meta protocolVersion 2030-01-01 → -32022 'Unsupported protocol version' (per-request version check by SDK)
- module-level container grep '^_?[A-Z_]+ … = {}|[]' src/ → 0 (control fires on scratch file); broader scan shows only constants (client.py:190, tools.py:101…); instance state client.py:612-614 is source state (quota, last success, search availability), client.py:387-445 rate bucket and TTL cache are source-derived
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random; tools registered at import (server.py:230-335)

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep 'initialize|notifications/initialized|InitializeResult|InitializationOptions' src/ → 0; grep 'mcp-session-id|session_manager|SessionManager|sessionId' src/ → 0 (negative controls: 10 and 9 hits in .venv/.../mcp/server/lowlevel/server.py)
- runtime: request with _meta protocolVersion 2030-01-01 → -32022 'Unsupported protocol version' (per-request version check by SDK)
- module-level container grep '^_?[A-Z_]+ … = {}|[]' src/ → 0 (control fires on scratch file); broader scan shows only constants (client.py:190, tools.py:101…); instance state client.py:612-614 is source state (quota, last success, search availability), client.py:387-445 rate bucket and TTL cache are source-derived
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random; tools registered at import (server.py:230-335)

**Geschlossen**
- Own code is stateless and version/caps are read per request by the SDK; the remaining gaps are the SDK's dual-era session issuance on HTTP and the missing test with counter-proof.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Mit `2026-07-28` fällt der Lebenszyklus weg, um den herum jeder MCP-Server bisher gebaut wurde. Zwei Entscheidungen, die zusammengehören:

### Remediation

Pass stateless_http=True (or otherwise disable the legacy handshake) in mcp.streamable_http_app and document it; add a test that interleaves two tool calls in different order across two Client sessions and assert identical results, and run it once against a deliberately stateful variant.

**Disposition:** The SDK (mcp 2.2.0) still answers a legacy initialize over HTTP and issues mcp-session-id; the server keeps no state of its own. Accepted until the SDK offers a switch; re-check at the next SDK minor.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-015` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-016

## Finding: ARCH-016 — server/discover ist implementiert — der RPC ist MUSS, nicht Kür

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-016` |
| **PDF-Reference** | SEP-2575 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Identity version is empty: MCPServer(...) at server.py:147-161 passes no version=; SDK default version '' (.venv/.../mcp/server/mcpserver/server.py:166) — package metadata version 0.1.0 is not used
- No test calls server/discover and checks versions, capabilities and identity separately (grep tests/ → 0); no Gegenprobe
- Capabilities advertise resources.subscribe/prompts although none exist (SDK default)
- Whether mcp 2.0.0 (the pinned lower bound) already ships server/discover and cache_hints was not verifiable offline

### Expected Behavior

- [ ] `server/discover` antwortet, über **jeden** bedienten Transportpfad (`ARCH-013`)
- [ ] Die Antwort nennt die unterstützten Protokollversionen als Liste, nicht als einzelnen String
- [ ] Die Antwort nennt die Server-Capabilities, inklusive `extensions` sofern welche geführt werden (`ARCH-021`)
- [ ] Die Antwort nennt die Server-Identität (Name, Version) — und die Version stammt aus den Paket-Metadaten, nicht aus einem Literal (`IDENT-002`)
- [ ] Stammt der RPC aus dem SDK, ist dessen Mindestversion im Manifest gepinnt
- [ ] Ein Test ruft `server/discover` auf und prüft alle drei Bestandteile einzeln — nicht nur, dass ein 200 zurückkam
- [ ] **Gegenprobe:** Der Test ist einmal gegen einen Server ohne den Handler gelaufen und hat dort angeschlagen

### Evidence

- src/discover_swiss_mcp/server.py:84 — CACHE_HINTS includes 'server/discover'; handler supplied by SDK (.venv/.../mcp/server/lowlevel/server.py:449,661-675), mcp 2.2.0 installed, pyproject.toml:34 mcp>=2,<3
- runtime HTTP: server/discover → supportedVersions ['2026-07-28'], capabilities {prompts, resources, tools}, instructions, resultType complete, ttlMs 300000, cacheScope public
- runtime stdio: same server/discover response via python -m discover_swiss_mcp
- runtime: _meta io.modelcontextprotocol/serverInfo = {name: 'discover_swiss_mcp', version: ''}

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:84 — CACHE_HINTS includes 'server/discover'; handler supplied by SDK (.venv/.../mcp/server/lowlevel/server.py:449,661-675), mcp 2.2.0 installed, pyproject.toml:34 mcp>=2,<3
- runtime HTTP: server/discover → supportedVersions ['2026-07-28'], capabilities {prompts, resources, tools}, instructions, resultType complete, ttlMs 300000, cacheScope public
- runtime stdio: same server/discover response via python -m discover_swiss_mcp
- runtime: _meta io.modelcontextprotocol/serverInfo = {name: 'discover_swiss_mcp', version: ''}

**Geschlossen**
- RPC answers on both transports with a version list and capabilities; identity version is blank and no test holds the three parts.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Wenn der `initialize`-Handshake wegfällt (`ARCH-015`), fehlt der Ort, an dem ein Server bisher gesagt hat, wer er ist und was er kann. `server/discover` ist dieser Ort — und die Spec ist an dieser Stelle asymmetrisch formuliert:

### Remediation

Pass version=__version__ (from package metadata) to MCPServer; add a test via mcp.Client asserting supportedVersions == ['2026-07-28'], 'tools' in capabilities, serverInfo.version == importlib.metadata.version('discover-swiss-mcp'); raise the lower bound to the first mcp 2.x that has cache_hints.

**Disposition:** serverInfo.version is empty: pass version=__version__ to MCPServer and test it on the wire.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-016` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-018

## Finding: ARCH-018 — resultType auf allen Results — «complete» ist kein Default, den man weglässt

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-018` |
| **PDF-Reference** | SEP-2322 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No test checks resultType on the wire (grep tests/ → 0); it rests entirely on SDK behaviour

### Expected Behavior

- [ ] `resultType` liegt auf jedem Result an — Erfolgs- **und** Fehlerpfad
- [ ] Der Wert ist `"complete"`, solange der Server kein MRTR führt
- [ ] Wird MRTR geführt, ist `"input_required"` ausschliesslich dem Zwischenstand vorbehalten (`HITL-006`)
- [ ] Stammt das Feld aus dem SDK, ist dessen Mindestversion im Manifest gepinnt
- [ ] Ein Test prüft das Feld am tatsächlichen Wire-Format, nicht am Rückgabewert der Python-Funktion — dazwischen liegt die Serialisierung, und genau dort geht es verloren

### Evidence

- runtime HTTP tools/call search without key (error path): result.isError true, resultType 'complete'
- runtime stdio tools/call source_status (success path): resultType 'complete', structuredContent present
- runtime: tools/list, server/discover, resources/list, prompts/list, resources/templates/list all carry resultType 'complete'
- grep resultType|result_type src/ → 0: field set by SDK (mcp 2.2.0); pyproject.toml:34 mcp>=2,<3

### Gemessen / Geschlossen / Offen

**Gemessen**
- runtime HTTP tools/call search without key (error path): result.isError true, resultType 'complete'
- runtime stdio tools/call source_status (success path): resultType 'complete', structuredContent present
- runtime: tools/list, server/discover, resources/list, prompts/list, resources/templates/list all carry resultType 'complete'
- grep resultType|result_type src/ → 0: field set by SDK (mcp 2.2.0); pyproject.toml:34 mcp>=2,<3

**Geschlossen**
- Field present on success and error paths via the SDK, value 'complete', no MRTR. Only the wire-format regression test is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Seit `2026-07-28` trägt **jedes** Result ein Pflichtfeld `resultType`, mit genau zwei Werten: `"complete"` für ein fertiges Ergebnis und `"input_required"` für den Zwischenstand eines Multi-Round-Trip-Requests (`HITL-006`).

### Remediation

Add a test using mcp.Client (or raw JSON-RPC over stdio) that asserts resultType == 'complete' on a successful and an isError tool result.

**Disposition:** resultType is set by the SDK; add one wire-format test so an SDK change is noticed.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-018` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-020

## Finding: ARCH-020 — ttlMs und cacheScope auf List- und Read-Ergebnissen, deterministische Reihenfolge

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-020` |
| **PDF-Reference** | SEP-2549 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- tools/list order comes from decorator registration order, not an explicit sort
- prompts/list, resources/list, resources/templates/list are served with ttlMs 0 (unjustified)
- Paged query results (page parameter) have no total sort key; relevance/distance ties decided upstream per call
- No two-page test (empty intersection + full union) and no Gegenprobe tests (set iteration, cacheScope 'session')

### Expected Behavior

- [ ] `ttlMs` und `cacheScope` liegen auf allen fünf Methoden an, sofern der Server sie bedient
- [ ] `ttlMs` ist begründet gewählt, nicht 0 und nicht willkürlich gross — ein Wert oberhalb der Änderungsfrequenz der Quelle liefert veraltete Werkzeuglisten
- [ ] Jeder gesetzte `cacheScope` trägt **einen der zwei Werte aus SEP-2549** — `"public"` oder `"private"`. Erhoben am ausgelieferten Result (Modus 2), nicht nur am Quelltext: Ein Literal kann auf dem Weg nach draussen noch durch ein Mapping laufen
- [ ] `cacheScope: "public"` steht ausschliesslich über aufruferunabhängigen Inhalten
- [ ] Bei `data_class != "Public Open Data"`: `resources/read` liefert `"private"`, und ein Test hält das fest
- [ ] `tools/list` liefert eine deterministische Reihenfolge, über **Prozessgrenzen** hinweg geprüft
- [ ] Die Reihenfolge stammt aus einer expliziten Sortierung, nicht aus der Registrierungsreihenfolge — letztere ändert sich mit jedem Refactoring des Imports
- [ ] Sofern der Server Query-Resultate paginiert: Der Sortierschlüssel ist **total** — bei Gleichstand entscheidet ein eindeutiger Zusatzschlüssel, nicht die Quelle
- [ ] Sofern paginiert: Ein Test über zwei aufeinanderfolgende Seiten belegt leere Schnittmenge **und** vollständige Vereinigung, gegen einen Bestand grösser als eine Seite
- [ ] Sofern der Server Datenresultate mit `ttlMs` versieht: Der Wert ist aus `source_freshness` abgeleitet (publizierte Kadenz, `Last-Modified`, `Cache-Control`) und auf die nächste Publikation gedeckelt — bei unbekannter Kadenz kurz, nicht komfortabel
- [ ] **Gegenprobe:** Der Reihenfolgetest ist einmal gegen eine Fassung mit `set`-Iteration gelaufen und hat dort angeschlagen; wo paginiert wird, ist der Seitentest einmal gegen einen nicht-totalen Sortierschlüssel gelaufen und hat dort angeschlagen; und die Werteprüfung ist einmal gegen ein Result mit `cacheScope: "session"` gelaufen und hat dort angeschlagen

### Evidence

- src/discover_swiss_mcp/server.py:75-85 — CACHE_HINTS tools/list and server/discover ttl_ms 300000, scope 'public', with rationale comment
- runtime tools/list: ttlMs 300000, cacheScope 'public'; prompts/list, resources/list, resources/templates/list: ttlMs 0, cacheScope 'private' (SDK defaults); all scopes within {public, private}
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random (negative control: a set of the same names changed order in each of 3 runs)
- grep orderBy|order_by|sort src/discover_swiss_mcp/*.py → 0: paged search results carry no explicit/total sort key
- grep tests/ for ttl|cacheScope|two-page overlap → 0

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:75-85 — CACHE_HINTS tools/list and server/discover ttl_ms 300000, scope 'public', with rationale comment
- runtime tools/list: ttlMs 300000, cacheScope 'public'; prompts/list, resources/list, resources/templates/list: ttlMs 0, cacheScope 'private' (SDK defaults); all scopes within {public, private}
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random (negative control: a set of the same names changed order in each of 3 runs)
- grep orderBy|order_by|sort src/discover_swiss_mcp/*.py → 0: paged search results carry no explicit/total sort key
- grep tests/ for ttl|cacheScope|two-page overlap → 0

**Geschlossen**
- Fields and values are present and valid, and order is stable across processes; the explicit sort, justified ttl on all served list methods, total sort key and the paging/counter-proof tests are missing (4 of 9 applicable).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Zwei Änderungen, die dieselbe Sache betreffen — was ein Client mit einer Antwort tun darf, nachdem er sie erhalten hat.

### Remediation

Sort tools explicitly by name (or add a test pinning the order across fresh processes), set cache hints for prompts/list and resources lists (or stop advertising them), send a total order to /search where supported (e.g. relevance then identifier) and add a two-page overlap test against a recorded result set.

**Disposition:** Sort tools/list explicitly by name instead of relying on registration order; add a test.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-020` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-021

## Finding: ARCH-021 — Extensions deklariert und versioniert — Tasks sind kein Kern-Feature mehr

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-021` |
| **PDF-Reference** | SEP-2663 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README.md / README.de.md do not state that the server carries no extensions (grep -i extension → 0; control: 21 hits in ARCH-021.md)

### Expected Behavior

- [ ] Führt der Server keine Extension, ist das im README in einem Satz festgehalten — nicht bloss unerwähnt
- [ ] Jede geführte Extension erscheint mit vollständiger, versionierter Kennung (`io.modelcontextprotocol/tasks`) in den Server-Capabilities
- [ ] Die Deklaration deckt sich in **beide** Richtungen mit dem Code
- [ ] Bei Tasks: Der Server spricht die Extension-Fassung (`tasks/get` / `tasks/update`), nicht `tasks/result` oder `tasks/list`
- [ ] Bei Tasks: Das README sagt, ob unaufgeforderte Task-Handles zurückgegeben werden, und die Tool-Descriptions sagen es bei den betroffenen Tools
- [ ] Eigene, nicht-offizielle Erweiterungen laufen unter einem eigenen Namensraum, nie unter `io.modelcontextprotocol/*`

### Evidence

- grep 'io.modelcontextprotocol/|extensions' src/ → only src/discover_swiss_mcp/net.py:144 (httpx request extensions={'sni_hostname': host}, not MCP) (control: hits .venv/.../mcp/shared/subscriptions.py)
- grep 'tasks/(get|update|result|list)|TaskHandle|task_id' src/ → 0 (control: hits .venv/.../mcp_types/_v2025_11_25/__init__.py)
- runtime server/discover capabilities: no extensions declared — declaration matches code in both directions

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep 'io.modelcontextprotocol/|extensions' src/ → only src/discover_swiss_mcp/net.py:144 (httpx request extensions={'sni_hostname': host}, not MCP) (control: hits .venv/.../mcp/shared/subscriptions.py)
- grep 'tasks/(get|update|result|list)|TaskHandle|task_id' src/ → 0 (control: hits .venv/.../mcp_types/_v2025_11_25/__init__.py)
- runtime server/discover capabilities: no extensions declared — declaration matches code in both directions

**Geschlossen**
- No extensions, no Tasks, no own namespace under io.modelcontextprotocol; only the one-sentence README statement is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der erste Umzugskandidat ist **Tasks**. In `2025-11-25` waren sie experimenteller Teil des Kerns; jetzt sind sie `io.modelcontextprotocol/tasks` — und die Extension ist nicht dieselbe API:

### Remediation

Add to README.md and README.de.md (e.g. in a 'MCP Protocol Version' section): 'This server speaks 2026-07-28 and carries no extensions.'

**Disposition:** README: one sentence that the server carries no extensions.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-021` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### ARCH-022

## Finding: ARCH-022 — Die Versionsquelle importiert das Paket-Root nicht

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-022` |
| **PDF-Reference** | Custom (Portfolio-Fundstücke i14y-mcp / bag-health-mcp, 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No leaf _version.py; client.py reads __version__ from the package root
- Root computes the version itself instead of importing it from a leaf module

### Expected Behavior

- [ ] Die Version steht in einem eigenen Modul (`_version.py` o. ä.), das **nichts** aus dem eigenen Paket importiert
- [ ] Kein Submodul liest `__version__` aus dem Paket-Root
- [ ] Das Paket-Root liest die Version ebenfalls aus diesem Modul, statt sie selbst zu ermitteln
- [ ] Die Korrektheit hängt **nicht** an der Reihenfolge der Zeilen in `__init__.py`
- [ ] KALT (Submodul zuerst) und WARM (Root zuerst) wurden in je **frischen** Interpretern gemessen, und **beide** Ergebnisse stehen in der Evidenz
- [ ] Der Pfad des deklarierten Konsolen-Skripts wurde bestimmt und mitgemessen — er ist der kalte
- [ ] Ein einzelner Lauf wurde **nicht** als Beleg für «kein Zyklus» gewertet
- [ ] Sofern ein Test die Eigenschaft hält: Er importiert in einem eigenen Prozess, nicht innerhalb der laufenden Suite

### Evidence

- src/discover_swiss_mcp/__init__.py:13-18 — __version__ from importlib.metadata in the package root; root imports only stdlib (importlib.metadata), no submodules
- src/discover_swiss_mcp/client.py:46 — 'from discover_swiss_mcp import __version__, net' (submodule reads version from the root); used in USER_AGENT client.py:52
- ls src/discover_swiss_mcp/_version.py → not present
- KALT (fresh interpreter, cwd /tmp): python -c 'import discover_swiss_mcp.client' → ok, USER_AGENT discover-swiss-mcp/0.1.0, kalt_exit=0
- WARM (fresh interpreter): import discover_swiss_mcp; import discover_swiss_mcp.client → ok, 0.1.0, warm_exit=0
- pyproject.toml:58-59 console script discover_swiss_mcp.server:main; fresh-interpreter import of discover_swiss_mcp.server → ok, script_exit=0

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/__init__.py:13-18 — __version__ from importlib.metadata in the package root; root imports only stdlib (importlib.metadata), no submodules
- src/discover_swiss_mcp/client.py:46 — 'from discover_swiss_mcp import __version__, net' (submodule reads version from the root); used in USER_AGENT client.py:52
- ls src/discover_swiss_mcp/_version.py → not present
- KALT (fresh interpreter, cwd /tmp): python -c 'import discover_swiss_mcp.client' → ok, USER_AGENT discover-swiss-mcp/0.1.0, kalt_exit=0
- WARM (fresh interpreter): import discover_swiss_mcp; import discover_swiss_mcp.client → ok, 0.1.0, warm_exit=0
- pyproject.toml:58-59 console script discover_swiss_mcp.server:main; fresh-interpreter import of discover_swiss_mcp.server → ok, script_exit=0

**Geschlossen**
- Both measurements pass and today there is no cycle because __init__.py imports no submodule; but the structure the check asks for (leaf version module, no submodule reading the root) is absent — adding 'from .server import mcp' to __init__ would create the i14y-style cycle.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Der Fall** (`i14y-mcp`): Das Submodul `client` braucht die Version für seinen User-Agent (`IDENT-001`). Es holt sie so:

### Remediation

Create src/discover_swiss_mcp/_version.py (stdlib-only) with the metadata lookup; import __version__ from it in __init__.py and client.py.

**Disposition:** Move __version__ into a leaf _version.py so client.py does not import the package root.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-022` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### DEP-001

## Finding: DEP-001 — Abhängigkeiten, deren Major-Wechsel den Import bricht, tragen eine Obergrenze

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DEP-001` |
| **PDF-Reference** | Custom (Portfolio-Fundstücke zurich-opendata-mcp 0.5.1 / swiss-energy-mcp; mcp 2.0.0 vom 2026-07-28) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- pydantic>=2 uncapped although the server subclasses its BaseModel across five modules (framework dependency per question 2)
- httpx>=0.27.0 uncapped although imported in two modules (client.py, net.py) with exception types and AsyncClient — not behind one adapter, no written rationale
- uvicorn imported directly (server.py:359) but not declared as a dependency — no bound of its own
- No automated cap-raising process for Python deps (Dependabot pip ecosystem missing)
- Caps on mcp (<3) and structlog (<27) currently have no measurable effect (next major not yet on the index)

### Expected Behavior

- [ ] Jede Abhängigkeit, aus deren Modulpfaden der Server importiert, trägt eine Obergrenze (`<N+1` oder enger)
- [ ] Das SDK bzw. Server-Framework ist gedeckelt — ausnahmslos
- [ ] Ungedeckelte Ranges sind auf Abhängigkeiten beschränkt, die hinter einer eigenen Schnittstelle liegen, und diese Entscheidung ist irgendwo aufgeschrieben
- [ ] Keine exakte Pinnung (`==`) in den Laufzeit-Abhängigkeiten der publizierten Distribution — Bereiche mit beiden Enden
- [ ] Jede Obergrenze ist **gemessen**: Die höchste vom Cap erlaubte Version wurde installiert, importiert und gegen die Suite gefahren (Modus 4a) — nicht auf die nächste runde Zahl gesetzt
- [ ] Für jede Obergrenze wurde der **Gegenversuch** geführt: Cap entfernt, gegen den Index aufgelöst, der nächste Major kommt herein (Modus 4b). Tut er das nicht, steht das als «Wirkung ungeprüft» im Report
- [ ] Die Abgrenzung zu `SDK-006` ist gewahrt: Ein Befund dort («Bound hält den alten Major fest») wurde nicht als Befund hier verbucht und umgekehrt
- [ ] Ein Prozess hebt Obergrenzen an (Dependabot / Renovate / dokumentierter Quartals-Durchgang); ein Deckel ohne diesen Prozess ist nur eine Verzögerung ohne Ende
- [ ] Die Auflösung wurde einmal **leer** durchgeführt und gegen das Lockfile gehalten (Modus 3) — nicht nur die Range gelesen
- [ ] Für jede offene Range steht im Report, ob sie geprüft und für vertretbar befunden wurde, oder ob niemand hingesehen hat. Beides ist ein Ergebnis, aber nicht dasselbe

### Evidence

- pyproject.toml:29-42 (mode 1 script): OK mcp>=2,<3; OK structlog>=24.1.0,<27; OFFEN httpx>=0.27.0; OFFEN pydantic>=2; OFFEN tzdata (win32 only); dev: OFFEN pytest/pytest-asyncio/respx, ruff==0.16.4 (dev extra only)
- imports (mode 2): httpx at client.py:43 and net.py:30; pydantic BaseModel subclassing in config.py:19, models.py:26, licenses.py:40, tools.py:32, client.py:44; uvicorn imported at server.py:359 but not declared (only transitively via mcp 'uvicorn>=0.31.1', no upper bound)
- mode 4a: installed mcp 2.2.0 and structlog 26.1.0 (highest under caps per fresh resolve) — pytest -m 'not live' → 215 passed
- mode 4b / mode 3: fresh venv, pip --dry-run --no-cache-dir 'mcp>=2' 'structlog>=24.1.0' 'pydantic>=2' 'httpx>=0.27.0' uvicorn → mcp 2.2.0, structlog 26.1.0, pydantic 2.13.5, httpx 0.28.1, uvicorn 0.54.0: no next major exists today, so both caps are 'Wirkung ungeprüft'; no lockfile in repo to compare
- .github/dependabot.yml — only github-actions ecosystem, no pip

### Gemessen / Geschlossen / Offen

**Gemessen**
- pyproject.toml:29-42 (mode 1 script): OK mcp>=2,<3; OK structlog>=24.1.0,<27; OFFEN httpx>=0.27.0; OFFEN pydantic>=2; OFFEN tzdata (win32 only); dev: OFFEN pytest/pytest-asyncio/respx, ruff==0.16.4 (dev extra only)
- imports (mode 2): httpx at client.py:43 and net.py:30; pydantic BaseModel subclassing in config.py:19, models.py:26, licenses.py:40, tools.py:32, client.py:44; uvicorn imported at server.py:359 but not declared (only transitively via mcp 'uvicorn>=0.31.1', no upper bound)
- mode 4a: installed mcp 2.2.0 and structlog 26.1.0 (highest under caps per fresh resolve) — pytest -m 'not live' → 215 passed
- mode 4b / mode 3: fresh venv, pip --dry-run --no-cache-dir 'mcp>=2' 'structlog>=24.1.0' 'pydantic>=2' 'httpx>=0.27.0' uvicorn → mcp 2.2.0, structlog 26.1.0, pydantic 2.13.5, httpx 0.28.1, uvicorn 0.54.0: no next major exists today, so both caps are 'Wirkung ungeprüft'; no lockfile in repo to compare
- .github/dependabot.yml — only github-actions ecosystem, no pip

**Geschlossen**
- SDK and structlog are capped and measured; pydantic, httpx and the undeclared uvicorn are open ranges on import-bearing dependencies, and no pip update automation exists. SDK-006 (mcp major) is judged separately and passes.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Der Fall** (2026-07-28): `mcp` 2.0.0 erschien und entfernte `mcp.server.fastmcp` ersatzlos. `swiss-energy-mcp` `0.3.3` deklarierte `mcp` ohne Obergrenze. Ab diesem Tag löste jedes frische `pip install` auf die 2er-Linie auf, und das Konsolen-Skript starb beim Start:

### Remediation

Set 'pydantic>=2,<3', 'httpx>=0.27.0,<1' (after 4a/4b measurement), declare 'uvicorn>=0.31.1,<1'; add a pip entry to .github/dependabot.yml; republish.

**Disposition:** Cap pydantic (<3) and httpx (<1); declare uvicorn explicitly with an upper bound; add pip to Dependabot.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DEP-001` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### DRIFT-002

## Finding: DRIFT-002 — Fallback verengt, erweitert nie — lieber ein Fehler als ein anderer Datensatz

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-002` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#33, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Fallbacks widen the answer set: search fallback drops `query` (returns everything near the point), accommodation fallback returns hotels regardless of stars/amenities/accessibility
- Which inputs were ignored is stated only in the hint string; `applied` (tools.py:897-917) has no field for ignored query/filters
- _accommodation_fallback and _ignored_accommodation_filters have no test (no test references them)
- tools.py:1724-1734 _schedule_entry falls back to entries[0] when no entry runs on from_date, which the event hit then reports as the overlapping entry; webcams live_url accepts link type 'WebLink' (tools.py:1863), only 'WebDetail' is verified as a live image

### Expected Behavior

- [ ] Jeder Auswahl-Fallback liefert denselben Datensatz-Typ wie der Primärpfad (gleiche Granularität, gleicher Zeitbezug, gleiche Entität)
- [ ] Fallbacks, die die Semantik ändern, sind entweder entfernt oder in der Antwort ausgewiesen (Feld, nicht nur Prosa)
- [ ] Wo kein semantisch gleichwertiger Kandidat existiert, wird eskaliert statt substituiert
- [ ] Ein Test hält fest, dass der Nicht-Fund ein Fehler ist — nicht nur, dass der Fund funktioniert
- [ ] Die Auswahlfunktion begründet im Docstring, was sie bewusst **nicht** nimmt

### Evidence

- src/discover_swiss_mcp/client.py:1035-1092 — resolve_area: exact name only; no exact match -> no id + suggestions; several exact matches -> largest with ambiguous=True and rivals in hint
- src/discover_swiss_mcp/tools.py:1480-1495, 1787-1797, 2004-2014, 2222-2232 — unresolved region: no search is run
- src/discover_swiss_mcp/tools.py:942-965 — search fallback without near/locality fetches nothing
- src/discover_swiss_mcp/tools.py:1013-1016, 1370-1379 — fallback responses carry provenance=list_fallback, degraded=search_unavailable fields; ignored query/filters named in hint prose
- src/discover_swiss_mcp/tools.py:1305-1324 — accommodation fallback ignores stars_min, garni, price_range, amenities, accessible
- tests/test_tools.py:670-681, tests/test_tools_p3.py:659 — tests that the non-find is not a substitution
- src/discover_swiss_mcp/client.py:966-981 — list_fallback docstring: 'Deliberately narrow, and deliberately not to be widened'

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:1035-1092 — resolve_area: exact name only; no exact match -> no id + suggestions; several exact matches -> largest with ambiguous=True and rivals in hint
- src/discover_swiss_mcp/tools.py:1480-1495, 1787-1797, 2004-2014, 2222-2232 — unresolved region: no search is run
- src/discover_swiss_mcp/tools.py:942-965 — search fallback without near/locality fetches nothing
- src/discover_swiss_mcp/tools.py:1013-1016, 1370-1379 — fallback responses carry provenance=list_fallback, degraded=search_unavailable fields; ignored query/filters named in hint prose
- src/discover_swiss_mcp/tools.py:1305-1324 — accommodation fallback ignores stars_min, garni, price_range, amenities, accessible
- tests/test_tools.py:670-681, tests/test_tools_p3.py:659 — tests that the non-find is not a substitution
- src/discover_swiss_mcp/client.py:966-981 — list_fallback docstring: 'Deliberately narrow, and deliberately not to be widened'

**Geschlossen**
- Area resolution escalates correctly and is tested. The search-refused fallback is declared (degraded/provenance fields) but widens semantics with the specifics in prose only, and its accommodation branch is untested.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Resilienz-Fallbacks sind Pflicht (Probe-Skill 3.1/3.5): Retry, Dump statt API, Cache statt Live. Alle diese lockern den **Weg** zum selben Datensatz. Es gibt aber eine zweite, verwandt aussehende Sorte, die etwas ganz anderes tut — sie lockert, **welcher Datensatz** geliefert wird:

### Remediation

Add applied['ignored'] = ['query', 'stars_min', ...] to both fallbacks; add a test for _accommodation_fallback asserting the ignored list; make _schedule_entry return None when no entry overlaps; restrict LIVE_LINK_TYPES to verified types.

**Disposition:** The list fallback widens the answer (search ignores query, accommodation ignores stars/amenities/accessible). Report the ignored inputs as a structured field (ignored_parameters), not only in hint, and test the accommodation fallback.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `DRIFT-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### DRIFT-004

## Finding: DRIFT-004 — Endpoint-Konstanten live verifiziert — ein Mock pinnt die eigene Annahme

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `DRIFT-004` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#35, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- List endpoints (the whole fallback path) and /status are not covered by any live test; /places, /foodEstablishments, /localbusinesses have never been called with the current select
- The live tests that exist have never been executed
- Live tests do not explicitly separate 404 (endpoint gone) from 5xx (transient)
- scripts/p3_stopgate_run.py and probes/probe_open.py are one-shot scripts, not a probe manifest run on a schedule

### Expected Behavior

- [ ] Jede Endpoint-Konstante wird von mindestens einem Live-Test oder einem Probe-Manifest abgedeckt
- [ ] Mocks registrieren gegen die importierte Konstante, nicht gegen ein wiederholtes URL-Literal
- [ ] Der Live-Test unterscheidet 404 (Endpoint weg) von 5xx (transient) — nur Ersteres ist ein Befund
- [ ] Die Abdeckung ist vollständig: kein Endpoint, der nur in Mocks vorkommt

### Evidence

- src/discover_swiss_mcp/config.py:23 and client.py:154-171 — endpoint inventory: /search, /vertices/{id}, /status, 14 list collections (5 used by the fallback, tools.py:749-755)
- tests/test_live.py:127-340 — live tests cover /search (via all search tools) and /vertices (test_detail_description_is_plain_text); none covers /status or any list endpoint
- probes/PROBE_OPEN_discover-swiss.md:16-27 — the 15-field LIST_SELECT was verified on /lodgingbusinesses, /civicStructures, /webcams only; fallback also reads /places, /foodEstablishments, /localbusinesses
- src/discover_swiss_mcp/client.py:123-126 — own comment: 'a field that is fine on /lodgingbusinesses can 400 on /webcams, and a 400 here fails the whole page'
- tests/conftest.py:36 — mocks registered against the constant-derived PINNED_BASE

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:23 and client.py:154-171 — endpoint inventory: /search, /vertices/{id}, /status, 14 list collections (5 used by the fallback, tools.py:749-755)
- tests/test_live.py:127-340 — live tests cover /search (via all search tools) and /vertices (test_detail_description_is_plain_text); none covers /status or any list endpoint
- probes/PROBE_OPEN_discover-swiss.md:16-27 — the 15-field LIST_SELECT was verified on /lodgingbusinesses, /civicStructures, /webcams only; fallback also reads /places, /foodEstablishments, /localbusinesses
- src/discover_swiss_mcp/client.py:123-126 — own comment: 'a field that is fine on /lodgingbusinesses can 400 on /webcams, and a 400 here fails the whole page'
- tests/conftest.py:36 — mocks registered against the constant-derived PINNED_BASE

**Geschlossen**
- Mocks are bound to the constant (criterion 2 met), but coverage is incomplete (fallback endpoints, /status), three fallback endpoints were never checked with the current select, and nothing live has run.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein `respx`-Mock wird gegen die eigene Konstante registriert:

### Remediation

Add a parametrised @pytest.mark.live contract canary over /status and each FALLBACK_ENDPOINTS entry with top=1 and LIST_SELECT, asserting status != 404 (fail) and 5xx (xfail/skip), and run it once now.

**Disposition:** Add live canaries for /status and for the list endpoints of the fallback (/places, /foodEstablishments, /localbusinesses, /civicStructures, /lodgingbusinesses) with the current select.

### Effort Estimate

S

### Dependencies / Blockers

Live-Lauf braucht einen Key; läuft lokal wie OPS-001.

### Verification After Fix

- Re-Audit von `DRIFT-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### DRIFT-005

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


### DRIFT-006

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


### DRIFT-008

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


### FID-001

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


### FID-002

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


### FID-003

## Finding: FID-003 — Leermenge von Abwesenheit unterscheidbar — keine Konfabulations-Einladung

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-003` |
| **PDF-Reference** | Custom (Portfolio-Fundstück termdat-mcp#11) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- get_details masks an upstream 4xx rejection (and a non-object payload) as 'Unknown identifier' — a failure reaches the model as a statement about the data (tools.py:1127-1130)
- 5xx/timeouts/429 and a refused /search end as well-formed results with returned=0 and `degraded` set, not in the error channel (tools.py:1066-1073 etc.); mitigated by the degraded field and its own hint, but the criterion asks for the error channel
- webcams_near description (server.py:307) licenses a conclusion from an empty result ('returns nothing — say so') instead of pointing to the hint/retry
- Only search's description has an explicit 'follow the hint before concluding'; get_details, find_accommodation, find_tours, explore_area descriptions do not say that no guessed answer may replace a missing hit

### Expected Behavior

- [ ] Ein leeres Result trägt ein maschinenlesbares Feld mit dem nächsten Schritt (`hint`, `next_step` o. ä.), nicht nur `returned: 0`
- [ ] Der Hinweis nennt **konkrete** nächste Versuche (Wildcard, Feld-Erweiterung, andere Sprache), keine Allgemeinplätze
- [ ] Keine Tool-Description enthält eine Formulierung, die eine Leermenge erklärt, entschuldigt oder als wahrscheinlich korrekt darstellt
- [ ] Falls ein Scope-Caveat inhaltlich nötig ist, fordert es zum Nachfassen auf, statt eine Schlussfolgerung zu lizenzieren
- [ ] Die Description sagt explizit, dass keine geratene Antwort an die Stelle eines fehlenden Treffers treten darf
- [ ] `not_found`-Verdikte (z. B. in QA-/Check-Tools) sind als «nicht in dieser Quelle» formuliert, nie als «falsch»
- [ ] Transport- und Autorisierungsfehler (Verbindungsabbruch, Timeout, 401/403, `421 Invalid Host header`, 5xx) enden im Fehlerkanal, nie als Result mit `returned: 0`
- [ ] Der Fehlerpfad trägt seinen eigenen nächsten Schritt — Konfiguration und Credentials prüfen —, nicht den Leermengen-Hinweis dieses Checks
- [ ] Auf `2026-07-28`, sofern das Tool `input_required` zurückgeben kann: Eine Rückfrage trägt **keinen** `hint` — sonst zeigt der nächste Schritt auf die Query, während gar nicht gesucht wurde
- [ ] Auf `2026-07-28`: Eine Rückfrage lässt `entries` **weg** statt es leer zu setzen — ein leeres `entries` ist bereits die Aussage «nichts gefunden»
- [ ] Auf `2026-07-28`: Eine Leermenge trägt **kein** `inputRequests` — sonst beschafft der Client eine Eingabe und retryt ins Leere

### Evidence

- src/discover_swiss_mcp/tools.py:171-199 — per-tool empty hints with concrete next steps (match='all', drop types, near instead of locality, explore_area; 'Do not conclude a place is absent from one empty result')
- src/discover_swiss_mcp/tools.py:653-694 — _paged_hint separates nothing-matched / past-the-end / all-withheld (with per-reason counts)
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — degraded states carry their own hint ('This says nothing about whether matching objects exist'), not the empty-set hint
- src/discover_swiss_mcp/server.py:211-222 — AuthorizationError/UpstreamRejectedError/NotFoundError become ToolError ('not an empty result — do not conclude anything about the data')
- src/discover_swiss_mcp/server.py:157-158 — server instructions: 'An empty result carries a hint — follow it before concluding that something does not exist'
- Registered description webcams_near (server.py:307): 'Outside Eastern Switzerland this tool returns nothing — say so and do not invent a webcam.'
- Runtime probe (scratchpad, respx): GET /vertices/eve_400 answering HTTP 400 -> get_details returns detail=None with hint 'Unknown identifier...' (tools.py:1127-1130 catches UpstreamRejectedError, which client.py:807 raises for every non-auth 4xx and client.py:896-899 for a non-object payload)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:171-199 — per-tool empty hints with concrete next steps (match='all', drop types, near instead of locality, explore_area; 'Do not conclude a place is absent from one empty result')
- src/discover_swiss_mcp/tools.py:653-694 — _paged_hint separates nothing-matched / past-the-end / all-withheld (with per-reason counts)
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — degraded states carry their own hint ('This says nothing about whether matching objects exist'), not the empty-set hint
- src/discover_swiss_mcp/server.py:211-222 — AuthorizationError/UpstreamRejectedError/NotFoundError become ToolError ('not an empty result — do not conclude anything about the data')
- src/discover_swiss_mcp/server.py:157-158 — server instructions: 'An empty result carries a hint — follow it before concluding that something does not exist'
- Registered description webcams_near (server.py:307): 'Outside Eastern Switzerland this tool returns nothing — say so and do not invent a webcam.'
- Runtime probe (scratchpad, respx): GET /vertices/eve_400 answering HTTP 400 -> get_details returns detail=None with hint 'Unknown identifier...' (tools.py:1127-1130 catches UpstreamRejectedError, which client.py:807 raises for every non-auth 4xx and client.py:896-899 for a non-object payload)

**Geschlossen**
- Empty-result diagnostics are strong and specific; transport failures carry a separate degraded marker. The concrete defect is get_details turning any non-auth 4xx into 'Unknown identifier', plus one description that pre-explains an empty result. MRTR/input_required criteria not applicable (grep for input_required in src/ empty; server does not return it).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein leeres Tool-Result ist mehrdeutig. Es kann heissen: der Begriff existiert nicht; die Query war zu eng; der Scope war eingeschränkt; die Syntax passte nicht. Das Modell sieht `[]` und muss raten — und es rät nicht neutral, sondern entlang dessen, was die Tool-Description ihm nahelegt.

### Remediation

In get_details catch UpstreamRejectedError only for the local identifier-pattern gate (raise a distinct exception there) and let upstream 4xx propagate to _fail; move the empty-result sentence of webcams_near into _webcams_empty_hint and replace it with 'Empty result: follow the hint'; add a one-line 'do not substitute a guess for a missing hit' to every data tool description.

**Disposition:** get_details reports any upstream 4xx as 'Unknown identifier'. Only 404 may say that; other 4xx become degraded with the status named.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### FID-004

## Finding: FID-004 — Parameter-Gruppen vollständig senden — Teilmengen erben Server-Defaults

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-004` |
| **PDF-Reference** | Custom (Portfolio-Fundstück termdat-mcp#11) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- match='all' is expressed by omitting searchFields, i.e. inheriting the upstream default rather than sending the full field set; a change of that default would narrow silently
- The live canary proving the narrowing has never been executed; only the 2026-09-17 probe measured the effect

### Expected Behavior

- [ ] Der Code kennt die vollständige Parameter-Gruppe als Konstante, nicht nur die jeweils angeforderte Teilmenge
- [ ] Jedes Mitglied der Gruppe wird bei jedem Request explizit gesetzt (`true` **oder** `false`)
- [ ] Ein Live-Test belegt, dass die Einschränkung messbar wirkt
- [ ] Der Default-Wert des Arguments entspricht dem tatsächlich gewünschten Set, nicht dem zufälligen API-Default
- [ ] Die Tool-Description nennt das Default-Set explizit, statt es als «alle» oder «Standard» zu umschreiben

### Evidence

- src/discover_swiss_mcp/tools.py:1041 — match='name' sends searchFields=name; match='all' sends nothing and relies on the index default
- probes/PROBE_REPORT_discover-swiss-mcp.md:89 — narrowing measured live: 'vegetarisch' 136 all / 0 name; 'Landesmuseum' 53 / 7 / 15
- tests/test_live.py:255-272 — live canary asserts name < all and name >= 3
- tests/test_tools.py:204 — unit test pins that searchFields is not sent for match='all'
- src/discover_swiss_mcp/server.py:232 — description names the default explicitly: 'matches whole words in name AND descriptions by default (match=\'all\')'
- src/discover_swiss_mcp/tools.py:130-149 — tour `kind` mapping from measured leafType/categoryTree sets (PROBE_TOURKINDS)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:1041 — match='name' sends searchFields=name; match='all' sends nothing and relies on the index default
- probes/PROBE_REPORT_discover-swiss-mcp.md:89 — narrowing measured live: 'vegetarisch' 136 all / 0 name; 'Landesmuseum' 53 / 7 / 15
- tests/test_live.py:255-272 — live canary asserts name < all and name >= 3
- tests/test_tools.py:204 — unit test pins that searchFields is not sent for match='all'
- src/discover_swiss_mcp/server.py:232 — description names the default explicitly: 'matches whole words in name AND descriptions by default (match=\'all\')'
- src/discover_swiss_mcp/tools.py:130-149 — tour `kind` mapping from measured leafType/categoryTree sets (PROBE_TOURKINDS)

**Geschlossen**
- No multi-flag parameter group (Field.* style) exists; the closest is searchFields, whose narrowing effect is measured and documented. Remaining gaps are reliance on the API default for 'all' and an unexecuted live check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die feinere Ausprägung von FID-001. Sendet ein Server eine **Teilmenge** einer zusammengehörigen Parameter-Gruppe, behalten die nicht gesendeten Mitglieder ihren serverseitigen Default. Das Ergebnis ist ein Parameter, der aussieht, als würde er steuern, tatsächlich aber nur addieren kann — nie einschränken.

### Remediation

Send an explicit searchFields list for match='all' (the measured searchable fields) or keep the omission but add the upstream default to the Default-Matrix with a live canary that runs; run test_match_name_narrows_the_search once.

**Disposition:** match='all' inherits the upstream default by omitting searchFields; send the explicit field list or pin the default with a live canary (the name/all canary covers half of it).

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `FID-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### FID-005

## Finding: FID-005 — Query-Syntax in der Tool-Description, nicht im README

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-005` |
| **PDF-Reference** | Custom (Portfolio-Fundstück termdat-mcp#11) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- The query language of searchText is not named, and it is not stated whether operators (*, ?, ~, quotes, AND/OR) work or are ignored; the probe never tested it
- The whole-word/compound claim is not backed by a probe measurement and has no concrete German compound example with a working alternative
- No live test for wildcard/prefix behaviour; no documentation of escaping or invalid-syntax behaviour
- Session rule violated: two tool descriptions (find_events, webcams_near) explain/handle an empty result set, which belongs in the hint

### Expected Behavior

- [ ] Jedes Tool mit freiem Such-Argument nennt die Abfragesprache namentlich in der Description
- [ ] Die unterstützten Operatoren sind konkret aufgeführt (`*`, `?`, `~`, Phrasen-Quoting, boolesche Operatoren)
- [ ] Die Matching-Granularität ist benannt (ganze Wörter / Substring / Präfix) — bei deutschsprachigen Quellen mit Kompositum-Beispiel
- [ ] Ein Live-Test belegt die Wildcard-Wirkung
- [ ] Falls Sonderzeichen escaped werden müssen, ist das dokumentiert — inklusive Verhalten bei ungültiger Syntax
- [ ] Die Description steht im Tool, nicht ausschliesslich im README

### Evidence

- src/discover_swiss_mcp/tools.py:285-286 — query field: 'Whole words only: \'Landesmuseum\' matches, \'Landesmus\' and parts of compounds do not.'
- Registered search description (list_tools, whitespace-normalised): '...matches whole words in name AND descriptions... Compounds are not found by their parts.' — granularity stated in the tool, not only README
- Registered descriptions scanned with /lucene|wildcard|\*|fuzzy|operator|syntax/ (negative control fired on 'Lucene syntax: * wildcard'): search has no query-language or operator mention (only hit '*' is 'excluded_*', 'fuzzy' is 'No fuzzy match' for locality)
- Registered find_events description (server.py:292): 'if it returns nothing, name a regional event calendar rather than concluding nothing is on'
- Registered webcams_near description (server.py:307): 'Outside Eastern Switzerland this tool returns nothing — say so and do not invent a webcam.'
- grep probes/*.md probes/*.py for wildcard|lucene|searchMode|prefix — no probe of query syntax; 'Landesmus' appears only in tools.py:285 (claim unmeasured)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:285-286 — query field: 'Whole words only: \'Landesmuseum\' matches, \'Landesmus\' and parts of compounds do not.'
- Registered search description (list_tools, whitespace-normalised): '...matches whole words in name AND descriptions... Compounds are not found by their parts.' — granularity stated in the tool, not only README
- Registered descriptions scanned with /lucene|wildcard|\*|fuzzy|operator|syntax/ (negative control fired on 'Lucene syntax: * wildcard'): search has no query-language or operator mention (only hit '*' is 'excluded_*', 'fuzzy' is 'No fuzzy match' for locality)
- Registered find_events description (server.py:292): 'if it returns nothing, name a regional event calendar rather than concluding nothing is on'
- Registered webcams_near description (server.py:307): 'Outside Eastern Switzerland this tool returns nothing — say so and do not invent a webcam.'
- grep probes/*.md probes/*.py for wildcard|lucene|searchMode|prefix — no probe of query syntax; 'Landesmus' appears only in tools.py:285 (claim unmeasured)

**Geschlossen**
- Matching granularity is in the tool description (criteria 3 and 6 met), but the query syntax is neither named nor probed, operators are unknown, and two descriptions carry empty-result explanations. 2 of 6 criteria met.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Wenn ein Such-Argument eine eigene Abfragesprache spricht — Lucene, CQL, SQL-Fragmente, Regex, Glob, SPARQL-Filter —, dann ist diese Sprache Teil der Aufrufkonvention und gehört in die Tool-Description. Steht sie nur im README, existiert sie für das Modell nicht: Das README wird nicht an den Kontext weitergereicht, die Description schon.

### Remediation

Probe /search searchText with 'Landesmus*', 'Landesmus', '"Landesmuseum Zürich"', 'Landesmuseum~' and record counts; state the outcome in the search/query description (e.g. 'plain words, no wildcard' or 'Lucene: * ? ~ work'); add a live test; move the empty-result sentences of find_events and webcams_near into EVENTS_EMPTY_HINT/_webcams_empty_hint.

**Disposition:** Name the query language of searchText and whether operators work (measure first), and remove the empty-result explanations from the find_events and webcams_near descriptions (they belong in hint). Changes the tool hashes.

### Effort Estimate

S

### Dependencies / Blockers

Ändert Tool-Descriptions → Tool-Hash-Snapshot im selben PR.

### Verification After Fix

- Re-Audit von `FID-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### FID-006

## Finding: FID-006 — Antwortstruktur und Feldnamen bestätigen, bevor gezählt wird

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `FID-006` |
| **PDF-Reference** | Custom (Portfolio-Fundstücke MCP Registry 2026-07 und zh-education-mcp / BISTA 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Root paths (values, data, facets) are not confirmed; a structural change becomes a valid empty result with the wildcard-style empty hint
- Fields read from hits (identifier, name, dataGovernance.origin, address.addressLocality, geo, lastModified) are never confirmed on the first entry
- No structure error type; error messages cannot name the keys that actually arrived
- No test holds structure/field names against a real response (live canaries unexecuted; unit fixtures come from recorded probes, which pin the 2026-09 shape but not today's)

### Expected Behavior

- [ ] Der Wurzelpfad der Antwort wird bestätigt, bevor gezählt wird — kein `.get(<Wurzelschlüssel>, [])`, das eine Strukturabweichung in eine Leermenge umschreibt
- [ ] Die vom Code **gelesenen** Felder werden auf dem ersten Eintrag bestätigt, nicht nur die Hülle darum
- [ ] Eine Abweichung endet in einem eigenen Fehlertyp (`UpstreamSchemaError` o. ä.), nicht in einem gültigen leeren Result
- [ ] Die Fehlermeldung nennt die **tatsächlich vorhandenen** Schlüssel — ohne sie ist der nächste Schritt Raten
- [ ] Die Prüfung deckt ausschliesslich, was der Code anfasst; ein zusätzliches optionales Feld upstream lässt sie grün
- [ ] Kein Feldzugriff im Code trägt eine Schreibweise, die die Quelle bereits gewechselt hat, und Endpunkte derselben Quelle mit **unterschiedlicher** Schreibweise werden nicht mit je einem eigenen Literal bedient
- [ ] Hält die Quelle ihre Schreibweise nicht stabil, wird sie an **genau einer** Stelle normalisiert — dort, wo die Rohzeile entsteht, nicht verstreut an den Lesestellen; die Funktion begründet im Docstring, **warum** sie existiert, sonst wird sie beim nächsten Refactoring wegoptimiert
- [ ] Normalisiert wird nur die **Schreibweise**, nicht die Identität des Namens — `anzahl_total` und `anzahlTotal` bleiben verschieden
- [ ] Mindestens ein Test hält Struktur **und** Feldnamen gegen die **echte** Antwort, nicht gegen ein Fixture (`DRIFT-004`, `OPS-009`)
- [ ] **Gegenprobe:** Der Strukturtest ist einmal gegen eine um eine Ebene verschobene Antwort gelaufen und hat dort angeschlagen; wird normalisiert, ist er zusätzlich gegen die jeweils andere Schreibweise gelaufen und hat die Zeile dort gefunden

### Evidence

- src/discover_swiss_mcp/client.py:848-850 — `payload = payload if isinstance(payload, dict) else {}`; facets likewise default to {}
- src/discover_swiss_mcp/client.py:858-861 — `values` defaults to [] when the key is missing or not a list
- src/discover_swiss_mcp/client.py:947-950 — list endpoints: `data` defaults to [] silently
- src/discover_swiss_mcp/client.py:483-490 — facet_values returns [] for an absent facet
- grep SchemaError|UpstreamSchema|UnexpectedPayload|StructureError in src/ — no hits (negative control: pattern fires on 'class UpstreamSchemaError')
- Runtime probe (scratchpad, respx): /search answering {'count':53,'value':[...]} (root key shifted) -> search_impl returns returned=0, upstream_count=53, degraded=None, hint 'No hit. Try: ...' (the FID-003 empty hint); control with 'values' returns 1 hit
- src/discover_swiss_mcp/client.py:896-899 — get_vertex does reject a non-object payload (only confirmation present)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:848-850 — `payload = payload if isinstance(payload, dict) else {}`; facets likewise default to {}
- src/discover_swiss_mcp/client.py:858-861 — `values` defaults to [] when the key is missing or not a list
- src/discover_swiss_mcp/client.py:947-950 — list endpoints: `data` defaults to [] silently
- src/discover_swiss_mcp/client.py:483-490 — facet_values returns [] for an absent facet
- grep SchemaError|UpstreamSchema|UnexpectedPayload|StructureError in src/ — no hits (negative control: pattern fires on 'class UpstreamSchemaError')
- Runtime probe (scratchpad, respx): /search answering {'count':53,'value':[...]} (root key shifted) -> search_impl returns returned=0, upstream_count=53, degraded=None, hint 'No hit. Try: ...' (the FID-003 empty hint); control with 'values' returns 1 hit
- src/discover_swiss_mcp/client.py:896-899 — get_vertex does reject a non-object payload (only confirmation present)

**Geschlossen**
- The recorded-probe fixtures are good, but the reader silently defaults on every root path; the runtime probe shows a shifted payload surfacing as 'No hit' with upstream_count 53. Criterion 5 (only what is touched) and case normalisation are moot since nothing is confirmed. Advisory check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Belegfall (MCP Registry, 2026-07).** Eine Abfrage lieferte konsequent nichts. Die Anfrage war einwandfrei, die Antwort ebenso — nur liegen die gesuchten Felder unter `servers[].server.*`, und gelesen wurde eine Ebene höher. Der Code war syntaktisch fehlerfrei und semantisch blind:

### Remediation

Add UpstreamSchemaError; in search()/list_endpoint() require 'values'/'data' (and 'facets' when facets were requested) and confirm identifier+name on values[0], raising with sorted(payload) keys; map it to a ToolError in server._fail; add a unit test with a shifted payload and a live structure canary.

**Disposition:** Confirm the root paths values/data/facets; a missing root key becomes a structural error (degraded: upstream_shape_changed), never an empty result.

### Effort Estimate

S

### Dependencies / Blockers

Neuer degraded-Wert braucht Envelope-Doku (models.py) und Tool-Hash-Update.

### Verification After Fix

- Re-Audit von `FID-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### FID-007

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


### IDENT-002

## Finding: IDENT-002 — __version__ aus der installierten Distribution, nicht von Hand gepflegt

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-002` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No version invariant test: tests/test_smoke.py:18-20 only asserts __version__ is a non-empty string; nothing compares __version__ with server.json or pyproject.toml
- Consequently no detuned-server.json counter-test, no editable-install hint in a failure message, no skip-without-install behaviour
- Observation outside the criteria: src/discover_swiss_mcp/server.py:147-161 builds MCPServer without version=__version__; serverInfo.version on the wire is '' (stdio initialize from the wheel-installed entry point returned {'name': 'discover_swiss_mcp', 'version': ''})

### Expected Behavior

- [ ] `__version__` wird über `importlib.metadata.version()` (bzw. das Sprach-Äquivalent) gelesen
- [ ] Kein Versionsliteral unter `src/` ausser dem Fallback-Marker (IDENT-005)
- [ ] **Kein Versionsliteral unter `tests/`** — ein Test, der die Nummer festnagelt, ist selbst eine Versions-Stelle
- [ ] Der Versions-Test vergleicht eine **Invariante** zwischen zwei unabhängig gepflegten Stellen (`__version__` gegen `server.json`), nicht `__version__` gegen eine aufgeschriebene Zahl
- [ ] Dieser Test wurde durch **Verstimmen von `server.json`** einmal rot gesehen — sonst ist unbelegt, dass er greift
- [ ] Ein Test vergleicht die installierten Metadaten gegen `pyproject.toml`
- [ ] Die Fehlermeldung dieses Tests nennt den Editable-Install-Fall
- [ ] Der Test wird ohne Installation **übersprungen**, nicht rot (sonst scheitert er im reinen Quell-Checkout)
- [ ] Bei Submodul-Importen in `__init__.py`: Versionsblock steht **vor** ihnen (Zirkelimport)
- [ ] Aus dem Bestehen dieses Checks wurde **nicht** auf die Identität des publizierten Pakets geschlossen — dafür sind `IDENT-001` (Modus 3) und `IDENT-006` zuständig

### Evidence

- src/discover_swiss_mcp/__init__.py:9-18 — __version__ = importlib.metadata.version('discover-swiss-mcp'), PackageNotFoundError fallback '0.0.0+source'
- grep -rnE '__version__\s*=\s*"[0-9]+\.[0-9]' src/ | grep -v '+' -> no hit; control '__version__ = "0.1.0"' matches
- grep -rnE '__version__\s*==\s*"[0-9]+\.[0-9]|==\s*"v?[0-9]+\.[0-9]+\.[0-9]+"' tests/ -> no hit; control 'assert __version__ == "0.3.0"' matches
- src/discover_swiss_mcp/__init__.py — imports no submodule, so no circular-import ordering risk
- Runtime: import discover_swiss_mcp -> __version__ 0.1.0 == pyproject.toml:7

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/__init__.py:9-18 — __version__ = importlib.metadata.version('discover-swiss-mcp'), PackageNotFoundError fallback '0.0.0+source'
- grep -rnE '__version__\s*=\s*"[0-9]+\.[0-9]' src/ | grep -v '+' -> no hit; control '__version__ = "0.1.0"' matches
- grep -rnE '__version__\s*==\s*"[0-9]+\.[0-9]|==\s*"v?[0-9]+\.[0-9]+\.[0-9]+"' tests/ -> no hit; control 'assert __version__ == "0.3.0"' matches
- src/discover_swiss_mcp/__init__.py — imports no submodule, so no circular-import ordering risk
- Runtime: import discover_swiss_mcp -> __version__ 0.1.0 == pyproject.toml:7

**Geschlossen**
- 5 of 10 criteria met: derivation is correct and literal-free, but no test holds the invariant, so the check's own counter-test cannot exist.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Portfolio-Sweep vom 2026-07-29 fand **20 von 30 Servern** mit abgedriftetem `__version__`:

### Remediation

Add tests/test_version.py: assert __version__ == json.loads(server.json)['version'] and == tomllib pyproject version (skip on '+source'), message mentions re-running pip install -e .; detune server.json once to see it fail. Pass version=__version__ to MCPServer.

**Disposition:** Add a test that __version__ equals pyproject.toml and server.json.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### IDENT-003

## Finding: IDENT-003 — Werte, die die Pipeline überschreibt, brauchen einen eigenen Check

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-003` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- packages[*].version is not enforced by CI: counter-test with packages[0].version = 9.9.9 -> validate_repo.py '0 ERROR, 0 WARN', exit 0 (check_release_artifacts.py:124-128 also compares only the top-level version)
- Published side cannot be read back: nothing published to PyPI or the MCP registry yet, and publish.yml has no registry step, so server.json is not shipped by the pipeline

### Expected Behavior

- [ ] `server.json → version` stimmt mit `pyproject.toml` überein
- [ ] **Jeder** `packages[*].version` stimmt überein, nicht nur der erste
- [ ] Ein CI-Check erzwingt das, nicht nur eine Konvention
- [ ] Der Check läuft ohne Projekt-Installation (schlanker Lint-Job genügt)
- [ ] Die Werte, die `publish.yml` zur Laufzeit überschreibt, sind dokumentiert
- [ ] Für jeden überschriebenen Wert existiert ein Check auf die committete Fassung
- [ ] **Und einer auf die geschriebene**: Der publizierte Wert wurde zurückgelesen — Registry gegen Index, oder die Transformation nachvollzogen (Modus 3)
- [ ] Die Transformation erfasst **jedes** Vorkommen des Wertes, nicht nur das erste (`packages[0]` ist kein `packages[*]`)
- [ ] Die Ableitung des Wertes ist gegen Nicht-Tag-Läufe abgesichert: Bei `workflow_dispatch` aus einem Branch ist `GITHUB_REF_NAME` der Branch-Name, und ein blindes `${VAR#v}` schreibt `main` als Version

### Evidence

- server.json:5 version 0.1.0 and server.json:15 packages[0].version 0.1.0 == pyproject.toml:7 0.1.0 (IDENT-003 Modus-1 script: both OK)
- scripts/validate_repo.py:394-402 — CI (ci.yml:70-71) raises ERROR on pyproject vs server.json top-level version drift; stdlib-only script (imports ast/json/re/subprocess/sys/pathlib)
- Counter-test in scratch copy: server.json version -> 9.9.9 gives '[A4] Versionsdrift' and exit 1
- scripts/check_release_artifacts.py:124-143 + publish.yml:38-42 — release gate compares server.json/pyproject and tag vs built version; a workflow_dispatch from a branch makes tag 'main' != version and stops the release
- grep -n "sed -i|jq '\.|yq -i|::set-output|GITHUB_REF_NAME" .github/workflows/ -> only publish.yml:42 (passes the tag to the checker); publish.yml overwrites no committed value

### Gemessen / Geschlossen / Offen

**Gemessen**
- server.json:5 version 0.1.0 and server.json:15 packages[0].version 0.1.0 == pyproject.toml:7 0.1.0 (IDENT-003 Modus-1 script: both OK)
- scripts/validate_repo.py:394-402 — CI (ci.yml:70-71) raises ERROR on pyproject vs server.json top-level version drift; stdlib-only script (imports ast/json/re/subprocess/sys/pathlib)
- Counter-test in scratch copy: server.json version -> 9.9.9 gives '[A4] Versionsdrift' and exit 1
- scripts/check_release_artifacts.py:124-143 + publish.yml:38-42 — release gate compares server.json/pyproject and tag vs built version; a workflow_dispatch from a branch makes tag 'main' != version and stops the release
- grep -n "sed -i|jq '\.|yq -i|::set-output|GITHUB_REF_NAME" .github/workflows/ -> only publish.yml:42 (passes the tag to the checker); publish.yml overwrites no committed value

**Geschlossen**
- Pipeline overwrites nothing, so the 'overwritten value' criteria are vacuous; committed values agree and the top-level field is CI-enforced. The package-entry version is exactly the half-bump case the check warns about and is unguarded.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Genau deshalb kann sie beliebig lange falsch sein. Bei `swiss-environment-mcp` stand sie von v0.2.3 bis v0.5.0 auf einer veralteten Nummer: funktional folgenlos, denn in der Registry landete jedes Mal korrekt die Tag-Version. Aufgefallen ist es niemandem, weil nichts brach.

### Remediation

Extend check_server_json in validate_repo.py (and check_release_artifacts.py) to loop over data.get('packages', []) and error on any packages[i].version != pyproject version.

**Disposition:** Extend the release check to packages[*].version in server.json.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### IDENT-004

## Finding: IDENT-004 — Dokumentierte Versionen erzwingen — Badges sind sonst dauerhaft falsch

| Feld | Wert |
|---|---|
| **Severity** | low |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-004` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No CI enforcement against pyproject: validate_repo.py C8 compares against the CHANGELOG release heading, is WARN-only, and returns silently when there is none (scripts/validate_repo.py:566-576); counter-test with README.de.md badge 0.0.9 -> '0 ERROR, 0 WARN', exit 0
- Hence no counter-test where a reverted badge breaks the check with exit 1

### Expected Behavior

- [ ] Jedes Versions-Badge stimmt mit `pyproject.toml` überein
- [ ] Alle README-Varianten geprüft (EN **und** DE), nicht nur die englische
- [ ] Ein CI-Check erzwingt das im selben Lauf wie IDENT-003
- [ ] Gegenprobe gefahren: zurückgedrehtes Badge bricht den Check mit `exit 1`

### Evidence

- README.md:7 and README.de.md:5 — shields badge version-0.1.0 == pyproject.toml:7 (check script: both OK; control pattern extracts 0.0.9 from a test badge)

### Gemessen / Geschlossen / Offen

**Gemessen**
- README.md:7 and README.de.md:5 — shields badge version-0.1.0 == pyproject.toml:7 (check script: both OK; control pattern extracts 0.0.9 from a test badge)

**Geschlossen**
- 2 of 4 criteria met: both badges are currently correct and both READMEs were checked, but nothing enforces it; pre-release the existing gate cannot fire.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Das Versions-Badge im README ist die Zahl, die Menschen als Erstes sehen — und die einzige Stelle im ganzen Repo, hinter der **nichts** steht. `publish.yml` synchronisiert das Manifest aus dem Tag, Tests prüfen den Code, aber ein Shields.io-Badge korrigiert niemand automatisch.

### Remediation

Compare README badges against pyproject version inside check_server_json (same run as the server.json check) and report ERROR; verify with a reverted badge.

**Disposition:** Enforce badge version against pyproject.toml, not only against the CHANGELOG heading.

### Effort Estimate

XS

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### IDENT-006

## Finding: IDENT-006 — Veröffentlichte Version ist der aktuelle Stand — kein Release-Gap

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-006` |
| **PDF-Reference** | Custom (Portfolio-Fundstück meteoswiss-mcp#31, 2026-07-30) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Never published (NOT_ON_INDEX): no index version and no release tag
- User-facing work has been unreleased for more than 7 days: 'P1: complete client layer' committed 2026-09-18 (8 days), followed by P2/P3 feature commits
- Release procedure (bump, tag vX.Y.Z, pypi environment approval) is not described in README or CONTRIBUTING; only the release gate condition is

### Expected Behavior

- [ ] Die auf dem Index veröffentlichte Version entspricht dem letzten Release-Tag
- [ ] Kein Release-Tag existiert, den der Index nicht hat (kein fehlgeschlagener Publish)
- [ ] Keine nutzerwirksamen Commits (`fix`, `feat`, `perf`, `revert`) älter als 7 Tage unveröffentlicht
- [ ] `[Unreleased]` im CHANGELOG ist entweder leer oder jünger als die Release-Kadenz — und beschreibt tatsächlich Unveröffentlichtes (`DRIFT-006`)
- [ ] Der Release-Prozess ist im README oder CONTRIBUTING beschrieben, inklusive des manuellen Schritts, falls es einen gibt
- [ ] Der Vergleich hat stattgefunden — Exit `127` der Probe ist `todo`, nicht Pass
- [ ] `IDENT-007` wurde **separat** beantwortet; ein Pass hier wurde nicht als Beleg dafür verbucht

### Evidence

- https://pypi.org/pypi/discover-swiss-mcp/json -> 404, control https://pypi.org/pypi/swiss-culture-mcp/json -> 200 (comparison took place: code NOT_ON_INDEX)
- git tag --list -> 0 tags; git ls-remote --tags origin -> none: no tag missing from the index
- pyproject.toml:7 version 0.1.0; README.md:21-27 'pre-release ... Release | none; version 0.1.0 is not published'; README.md:36-38 release gate = written search confirmation from discover.swiss
- CHANGELOG.md:8-11 — [Unreleased] 'Not released. Release gate: ...' describes exactly the unreleased state
- .github/workflows/publish.yml:5-9 — publish pipeline exists (tag push v*, workflow_dispatch)
- IDENT-007 answered separately (not_verified)

### Gemessen / Geschlossen / Offen

**Gemessen**
- https://pypi.org/pypi/discover-swiss-mcp/json -> 404, control https://pypi.org/pypi/swiss-culture-mcp/json -> 200 (comparison took place: code NOT_ON_INDEX)
- git tag --list -> 0 tags; git ls-remote --tags origin -> none: no tag missing from the index
- pyproject.toml:7 version 0.1.0; README.md:21-27 'pre-release ... Release | none; version 0.1.0 is not published'; README.md:36-38 release gate = written search confirmation from discover.swiss
- CHANGELOG.md:8-11 — [Unreleased] 'Not released. Release gate: ...' describes exactly the unreleased state
- .github/workflows/publish.yml:5-9 — publish pipeline exists (tag push v*, workflow_dispatch)
- IDENT-007 answered separately (not_verified)

**Geschlossen**
- 4 of 7 criteria met. The gap is deliberate and documented (release held until discover.swiss confirms the search entitlement), and the release process is set up rather than missing, so this is NOT_ON_INDEX by design, not a forgotten publish. It stays a finding until the first release.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Das ist eine eigene Fehlerklasse, und die unbequemste der Kategorie: Ein Repository kann grün, auditiert und vollständig korrigiert sein, während jedes `pip install` weiterhin das kaputte Release ausliefert. Nichts widerspricht dem, denn CI testet den Branch, nie das Artefakt. Der Server ist repariert; die Nutzenden merken nichts davon.

### Remediation

Document the release steps (bump pyproject/server.json, CHANGELOG section, tag v0.1.0, approve the pypi environment, verify from the index) in CONTRIBUTING.md; publish as soon as the entitlement gate clears.

**Disposition:** Not published on purpose: the release waits for discover.swiss's written confirmation of the search entitlement (README Status).

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OBS-001

## Finding: OBS-001 — Protocol vs. Execution Errors: korrekte Trennung

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-001` |
| **PDF-Reference** | Sec 6.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Unknown tool is answered as a tool result with isError=true instead of a JSON-RPC protocol error (-32601); this is mcp 2.2.0 MCPServer behaviour (exceptions.py docstring: SDK raises ToolError for unknown tool names), but the server does not override it — pass criterion 'standardised codes for protocol-level errors' not met
- No test covers the protocol-error path (unknown tool); grep for no_such_tool/unknown tool/-32601 in tests/ returns nothing
- Upstream-unreachable/quota states are returned as isError=false results with degraded+hint rather than isError=true; model-actionable, but deviates from the check's table (API down -> isError:true)

### Expected Behavior

- [ ] Tool-Handler fangen anwendungsspezifische Fehler (FileNotFound, RateLimit, InvalidArgument) ab
- [ ] Anwendungsfehler werden mit `isError: true` in `tool-result` zurückgegeben (nicht als JSON-RPC-Error)
- [ ] **Input- und Schema-Validierungsfehler laufen über den Execution-Pfad**, nicht über JSON-RPC (SEP-1303) — gilt auf beiden Baselines
- [ ] Die Fehlermeldung eines Validierungsfehlers nennt das betroffene Feld und den erwarteten Wertebereich; ohne das ist der nächste Versuch geraten
- [ ] Standardisierte Fehlercodes für Protocol-Level-Errors
- [ ] Auf `mcp_spec_version: 2026-07-28`: keine eigenen Codes im reservierten Bereich `-32020`…`-32099`; «resource not found» ist `-32602`, nicht `-32002`
- [ ] Mindestens 1 dokumentierter Test deckt Execution-Error-Pfad ab
- [ ] Mindestens 1 dokumentierter Test deckt Protocol-Error-Pfad ab (falsches Tool)
- [ ] Mindestens 1 Test belegt, dass ein **ungültiges Argument** als Execution-Error zurückkommt und nicht als JSON-RPC-Error

### Evidence

- src/discover_swiss_mcp/server.py:200-222 — _fail() logs the original, re-raises a masked ToolError; SDK turns ToolError into CallToolResult isError=true
- src/discover_swiss_mcp/server.py:236-242 — every tool body wrapped in try/except Exception -> _fail (same pattern at 251-257, 266-272, 281-287, 296-302, 311-317, 326-332, 341-349)
- src/discover_swiss_mcp/tools.py:697-705,708-716 — operational states (quota_exhausted, upstream_unreachable, search_unavailable) returned as structured result with degraded+hint, never as JSON-RPC error
- src/discover_swiss_mcp/tools.py:387, 275, 1641-1643 — input validators raise ValueError naming the field; arrive as execution errors
- runtime (in-memory Client, mcp 2.2.0): search params.page=-5 -> is_error=True, text names 'params.page' and 'greater than or equal to 1'; find_accommodation without near/locality -> is_error=True, 'Give `near` or `locality`'
- runtime (real stdio, python -m discover_swiss_mcp): tools/call no_such_tool -> result isError=true 'Unknown tool: no_such_tool', NOT a JSON-RPC error object
- tests/test_server.py:179-188 — missing key: execution-error path tested (is_error True, message names DISCOVER_SWISS_KEY)
- tests/test_server.py:191-196 — invalid argument returns is_error True and makes no upstream call
- grep -rnE '-320[2-9][0-9]|-3200[0-9]|-3201[0-9]|-32002' src/ -> no hit (exit 1); control 'code=-32021' matches -> no custom codes in the reserved range

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:200-222 — _fail() logs the original, re-raises a masked ToolError; SDK turns ToolError into CallToolResult isError=true
- src/discover_swiss_mcp/server.py:236-242 — every tool body wrapped in try/except Exception -> _fail (same pattern at 251-257, 266-272, 281-287, 296-302, 311-317, 326-332, 341-349)
- src/discover_swiss_mcp/tools.py:697-705,708-716 — operational states (quota_exhausted, upstream_unreachable, search_unavailable) returned as structured result with degraded+hint, never as JSON-RPC error
- src/discover_swiss_mcp/tools.py:387, 275, 1641-1643 — input validators raise ValueError naming the field; arrive as execution errors
- runtime (in-memory Client, mcp 2.2.0): search params.page=-5 -> is_error=True, text names 'params.page' and 'greater than or equal to 1'; find_accommodation without near/locality -> is_error=True, 'Give `near` or `locality`'
- runtime (real stdio, python -m discover_swiss_mcp): tools/call no_such_tool -> result isError=true 'Unknown tool: no_such_tool', NOT a JSON-RPC error object
- tests/test_server.py:179-188 — missing key: execution-error path tested (is_error True, message names DISCOVER_SWISS_KEY)
- tests/test_server.py:191-196 — invalid argument returns is_error True and makes no upstream call
- grep -rnE '-320[2-9][0-9]|-3200[0-9]|-3201[0-9]|-32002' src/ -> no hit (exit 1); control 'code=-32021' matches -> no custom codes in the reserved range

**Geschlossen**
- 7 of 9 criteria met. Classification of execution vs validation errors is correct and tested (SEP-1303 satisfied). The protocol-error side is missing: unknown tool comes back as isError result (SDK default) and no test pins the protocol-error path.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die MCP-Spezifikation fordert eine strikte Trennung zwischen zwei Fehler-Typen. Werden sie verwechselt, kann das LLM den Fehler nicht korrekt interpretieren und bricht in eine Halluzinations- oder Sackgassen-Schleife.

### Remediation

Add a test that calls an unknown tool and asserts the observed contract; if the target is spec conformance, map unknown-tool to a JSON-RPC -32601 (e.g. raise MCPError in a call_tool override) or document the SDK behaviour as accepted. Optionally set isError=true alongside degraded for upstream_unreachable/quota states.

**Disposition:** An unknown tool is answered as isError result instead of JSON-RPC -32601; this is mcp 2.2.0 MCPServer default behaviour, not server code. Revisit at the next SDK minor.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-001` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OBS-003

## Finding: OBS-003 — Structured Logging mit RFC 5424 Severity-Stufen

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-003` |
| **PDF-Reference** | Sec 6.3 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Only three distinct severities in use (info, warning, error/exception); debug is never emitted — criterion 'at least 4 levels (debug, info, warning, error)' not met
- Bound context has tool + correlation_id but no session_id / client identity

### Expected Behavior

- [ ] Structured Logger (structlog/pino/loguru) im `dependencies`
- [ ] JSON oder logfmt als Output-Format
- [ ] Mindestens 4 Severity-Stufen aktiv genutzt (debug, info, warning, error)
- [ ] Pro Tool-Call: bound context (tool name, session_id, correlation_id)
- [ ] Keine `print()`-Statements im Tool-Code (siehe OBS-004 für stdio)

### Evidence

- pyproject.toml:37 — structlog>=24.1.0,<27 in [project].dependencies
- src/discover_swiss_mcp/logging_config.py:68-82 — structlog JSONRenderer, add_log_level, ISO timestamp
- src/discover_swiss_mcp/logging_config.py:93-95 — tool_logger binds tool name and a fresh correlation_id per call; used at server.py:236,251,266,281,296,311,326,341
- grep of logger/log calls in src/: info (12), warning (6), error (4), exception (1); no debug
- grep -rnE '\bprint\(|sys\.stdout' src/ -> no hit (exit 1); control 'print("hi")' matches
- runtime: stderr lines are single JSON objects with event/level/timestamp fields (server start)

### Gemessen / Geschlossen / Offen

**Gemessen**
- pyproject.toml:37 — structlog>=24.1.0,<27 in [project].dependencies
- src/discover_swiss_mcp/logging_config.py:68-82 — structlog JSONRenderer, add_log_level, ISO timestamp
- src/discover_swiss_mcp/logging_config.py:93-95 — tool_logger binds tool name and a fresh correlation_id per call; used at server.py:236,251,266,281,296,311,326,341
- grep of logger/log calls in src/: info (12), warning (6), error (4), exception (1); no debug
- grep -rnE '\bprint\(|sys\.stdout' src/ -> no hit (exit 1); control 'print("hi")' matches
- runtime: stderr lines are single JSON objects with event/level/timestamp fields (server start)

**Geschlossen**
- 3 of 5 criteria fully met (structured logger dep, JSON output, no print); level coverage and session binding short.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: MCP-Server-Logs müssen strukturiert sein (JSON oder logfmt), nicht plaintext. Das ermöglicht Aggregation in Datadog/Splunk/Loki ohne Regex-Parsing, korrelierte Suche über Correlation-IDs, und konsistente Severity-Filterung.

### Remediation

Add debug-level events at useful points (cache hit/miss, request params after sanitisation) and bind the MCP session/request id from ctx in tool_logger.

**Disposition:** Emit debug events on the request path (cache hit/miss, fallback step).

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OBS-007

## Finding: OBS-007 — Fehler-Details bleiben nach innen diagnostizierbar

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OBS-007` |
| **PDF-Reference** | Custom (Portfolio-Fundstück swiss-efv-mcp#16) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Messages after exhausted retries do not state the number of attempts (client.py:737, 743, 796, 800)
- Unreachable/5xx messages name the service ('discover.swiss') but not the endpoint path; path is only in the per-retry log events
- No test pins the message for str(exc)=='' — tests/test_client.py:258-269 use ConnectError('no route')/ReadTimeout('slow') and only assert 'discover.swiss' in the message

### Expected Behavior

- [ ] Meldungen, die der Server für sich behält (Log **und** intern geworfene Exceptions), nennen den **Exception-Typ**, nicht nur `str(exc)`
- [ ] Bei leerem `str(exc)` bleibt ein vollständiger Satz stehen — ein Fallback wie `or "no further detail"` oder ein Format, das ohne die Message auskommt
- [ ] Das **Ziel** ist benannt (Host, Endpoint, Datensatz-Key) — ohne Query-String, Header oder Credentials
- [ ] Nach erschöpften Retries steht die **Anzahl Versuche** in der Meldung — «nach Retries» allein sagt nicht, ob zwei oder zwanzig
- [ ] `raise ... from exc` verkettet die Ursache, damit der ursprüngliche Traceback nicht verloren geht
- [ ] Richtung nach aussen bleibt maskiert: Der Detailtext taucht **nicht** im Tool-Result auf (`OBS-002` gilt unverändert)
- [ ] Mindestens ein Test prüft den Meldungsinhalt für den Fall `str(exc) == ""` — ohne ihn verfällt der Text beim nächsten Refactoring unbemerkt

### Evidence

- src/discover_swiss_mcp/client.py:735-743 — network failure after retries: UpstreamUnavailableError(f'discover.swiss is not reachable ({type(exc).__name__}).') from exc — type named, cause chained, no str(exc)
- src/discover_swiss_mcp/client.py:725-728 — total-budget timeout message names the budget, chained from exc
- src/discover_swiss_mcp/client.py:745, 801 — retry log events carry path, reason=type(exc).__name__ / status, delay
- runtime (respx, side_effect ConnectTimeout(''), ReadTimeout(''), ConnectError('')): messages 'discover.swiss is not reachable (ConnectTimeout).' etc., __cause__ is the original type; 5xx exhaustion -> 'discover.swiss answered HTTP 503.'
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — outward direction masked: the model sees fixed DEGRADED_HINTS, not the exception text

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:735-743 — network failure after retries: UpstreamUnavailableError(f'discover.swiss is not reachable ({type(exc).__name__}).') from exc — type named, cause chained, no str(exc)
- src/discover_swiss_mcp/client.py:725-728 — total-budget timeout message names the budget, chained from exc
- src/discover_swiss_mcp/client.py:745, 801 — retry log events carry path, reason=type(exc).__name__ / status, delay
- runtime (respx, side_effect ConnectTimeout(''), ReadTimeout(''), ConnectError('')): messages 'discover.swiss is not reachable (ConnectTimeout).' etc., __cause__ is the original type; 5xx exhaustion -> 'discover.swiss answered HTTP 503.'
- src/discover_swiss_mcp/tools.py:208-222, 697-705 — outward direction masked: the model sees fixed DEGRADED_HINTS, not the exception text

**Geschlossen**
- 5 of 7 criteria met. The dangerous pattern (f'...: {exc}') is absent; type and cause survive empty httpx messages (verified at runtime). Missing: attempt count, endpoint in final message, and a test holding the text.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Genau das ist der Fall, sobald eine Exception in eine eigene Meldung interpoliert wird:

### Remediation

Include attempts and path in the final message, e.g. f'discover.swiss not reachable after {retry_index+1} attempts: {type(exc).__name__} (path={path})', and add a respx test with httpx.ConnectTimeout('') asserting type name, path, attempt count and __cause__.

**Disposition:** Name the attempt count and the endpoint path in the final error after exhausted retries.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OBS-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OBS-008

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


### OPS-001

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


### OPS-002

## Finding: OPS-002 — Doku-Standard: bilingualer README, ASCII-Diagramm, Limits-Sektion

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-002` |
| **PDF-Reference** | Anhang C2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No ASCII/Mermaid architecture diagram: README 'Architecture decision' (README.md:197-218) is prose; the only box-drawing characters are the file tree (README.md:254-275); grep for ┌|└|▼|mermaid|--> finds nothing else (control '┌──┐' matches)
- Security section (README.md:315-319) only links SECURITY.md; data class, auth model and trifecta assessment are not stated there
- CONTRIBUTING.md is English only; no CONTRIBUTING.de.md

### Expected Behavior

- [ ] `README.md` enthält alle 8 Pflicht-Sektionen (Anchor-Demo, Installation, Tools, Config, Security, Architektur-Diagramm, Limits, Lizenz)
- [ ] `README.de.md` enthält die gleichen Top-Level-Sektionen
- [ ] Anchor-Demo-Query ist konkret und natürlich-sprachlich
- [ ] ASCII-Architekturdiagramm ist vorhanden (oder Mermaid-Diagramm als gleichwertig)
- [ ] Bekannte-Limits-Sektion ist explizit (mindestens 3 Limits genannt)
- [ ] CHANGELOG.md im Keep-a-Changelog-Format (Synergie zu ARCH-012)
- [ ] CONTRIBUTING.md vorhanden, bilingual

### Evidence

- README.md:47-66 — 'Anchor demo queries', three concrete natural-language questions with tool chains (docs/DEMO.md)
- README.md:124-132 — Installation (git clone + pip install -e); README.md:151 Available Tools; README.md:240-252 Configuration table
- README.md:220-238 — Known limitations, 12 numbered items
- README.md:321-326 — License (software MIT, data per provider)
- README.de.md:45,122,150,221,241,317,323 — same top-level section set in German (Anker-Abfragen, Installation, Verfügbare Tools, Bekannte Einschränkungen, Konfiguration, Sicherheit, Lizenz)
- CHANGELOG.md:1-8 — Keep a Changelog header, [Unreleased] with ### Added

### Gemessen / Geschlossen / Offen

**Gemessen**
- README.md:47-66 — 'Anchor demo queries', three concrete natural-language questions with tool chains (docs/DEMO.md)
- README.md:124-132 — Installation (git clone + pip install -e); README.md:151 Available Tools; README.md:240-252 Configuration table
- README.md:220-238 — Known limitations, 12 numbered items
- README.md:321-326 — License (software MIT, data per provider)
- README.de.md:45,122,150,221,241,317,323 — same top-level section set in German (Anker-Abfragen, Installation, Verfügbare Tools, Bekannte Einschränkungen, Konfiguration, Sicherheit, Lizenz)
- CHANGELOG.md:1-8 — Keep a Changelog header, [Unreleased] with ### Added

**Geschlossen**
- 4 of 7 criteria met. Anchor demo, limits, bilingual parity and changelog format are good; diagram, security summary and bilingual CONTRIBUTING missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: ARCH-011 verlangt die Existenz von `README.md`, `README.de.md`, `CHANGELOG.md` als Files. OPS-002 verlangt **Inhalt-Disziplin** für diese Files — nicht nur Existenz.

### Remediation

Add a one-screen ASCII data-flow diagram (client -> stdio/HTTP -> server -> net.safe_request -> api.discover.swiss) to both READMEs, extend the Security section with data class (public open data), auth model (BYO upstream key, no client auth, local only) and trifecta rating, and add CONTRIBUTING.de.md.

**Disposition:** Add a Mermaid architecture diagram (search-centred, list fallback) to the README; CONTRIBUTING stays English.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OPS-003

## Finding: OPS-003 — Phasenarchitektur: Read-only First, dann Write, dann Multi-Agent

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-003` |
| **PDF-Reference** | Anhang C4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No phase declaration: grep -iE 'phase|roadmap|read.only.first' over README.md, README.de.md, CHANGELOG.md, docs/*.md -> no hit (control 'Phase 1' matches). The P1-P4 labels in commits/CHANGELOG are build milestones, not OPS-003 phases
- No roadmap file (find for *phase*/*roadmap* outside .venv -> none)
- No documented phase-transition prerequisites (audit run, ISDS, DSG record)
- Phase transitions not recorded in CHANGELOG

### Expected Behavior

- [ ] Aktuelle Phase explizit im README deklariert (Phase 1 / 2 / 3)
- [ ] Phase entspricht den tatsächlichen Tool-Annotations (kein Phase-1-Server mit destruktiven Tools)
- [ ] Roadmap-File mit phasenspezifischen Tasks vorhanden
- [ ] Phase-Übergang erfordert dokumentierte Voraussetzungen:
  - Phase 1 → 2: Audit-Run, ISDS, DSG-Verarbeitungsverzeichnis abgeschlossen
  - Phase 2 → 3: Semantic Layer, Identity-Resolution, GL-Sign-off, Datenschutzbeauftragte:r-Sign-off
- [ ] Phase-Übergänge im CHANGELOG dokumentiert (Synergie zu ARCH-012)

### Evidence

- src/discover_swiss_mcp/server.py:170-179 — all 8 tools annotated readOnlyHint=True, destructiveHint=False
- tests/test_server.py:103-108 — test asserts read_only_hint True / destructive_hint False for every tool
- grep -rnE 'destructiveHint.*True' src/ -> no hit

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:170-179 — all 8 tools annotated readOnlyHint=True, destructiveHint=False
- tests/test_server.py:103-108 — test asserts read_only_hint True / destructive_hint False for every tool
- grep -rnE 'destructiveHint.*True' src/ -> no hit

**Geschlossen**
- 1 of 5 criteria met: the server is de facto Phase 1 (read-only, verified), but the phase is not declared and there is no roadmap or gate.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Anhang sagt klar: «Die häufigste Ursache von MCP-Sicherheitsvorfällen 2025/26 war: ‹Wir haben gleich Schreibzugriffe gebaut, weil es ging.›»

### Remediation

Add a '## Phase' section to both READMEs ('Phase 1: read-only wrapper' with status table) and docs/roadmap.md listing Phase 1 completion items and Phase 2/3 prerequisites; note the declaration in CHANGELOG.

**Disposition:** Declare the phase (read-only, P4 hardening) and the phase gates P1-P4 plus the release gate in the README.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OPS-005

## Finding: OPS-005 — Pipeline unterscheidet «bestanden» von «nicht gelaufen»

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-005` |
| **PDF-Reference** | Custom (Portfolio-Fundstück mcp-continuous-auditor#29) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Copied portfolio scripts are only format-stable at the local line-length 100: ruff format --check --line-length {88,110,120} scripts/ fails for validate_repo.py, check_release_artifacts.py, gen_tool_hashes.py, p2/p3 run scripts; no CI step enforces multi-width stability
- validate_repo.py C8 version-anchor check is silent without a release heading (scripts/validate_repo.py:566-576): 'not checked' collapses into 'OK'. Counter-test in a scratch copy: README.de.md badge set to 0.0.9 -> '0 ERROR, 0 WARN', exit 0
- No in-repo evidence that gates were verified in both directions (no documented counter-test)

### Expected Behavior

- [ ] Mindestens ein committeter Workflow führt die Testsuite aus, ausgelöst durch `push` und `pull_request` — nicht nur als `.template` für andere Repos
- [ ] Jeder Schritt mit `continue-on-error`, bedingtem `if:` oder `|| true` hat eine **sichtbare Folge**, wenn er ausbleibt: eine Zeile im Bericht, ein Artefakt, eine Annotation
- [ ] Kein Test wird wegen einer fehlenden Abhängigkeit übersprungen, die CI installieren könnte
- [ ] `run:`-Blöcke mit Pipes setzen `pipefail`, sonst maskiert der letzte Befehl den Exit-Code
- [ ] Jedes Gate ist in beide Richtungen verifiziert: Es schlägt an, wenn es soll, und schweigt, wenn es soll
- [ ] Ein Artefakt, das zwischen Repos kopiert wird, ist gegen **jede** dort genutzte Werkzeug-Konfiguration geprüft — nicht nur gegen die lokale
- [ ] Linter und Formatter laufen über **alle** Verzeichnisse mit eigenem Code — insbesondere über `scripts/`, wo die Prüfskripte der übrigen Gates liegen
- [ ] Jeder konfigurierte Regelsatz wird von mindestens einem Workflow auch aufgerufen
- [ ] Kein Gate ist per Kommentar stillgelegt; wo es sein muss, existiert stattdessen ein verfolgbarer Eintrag
- [ ] Der Bericht unterscheidet «kein Befund» von «nicht geprüft»

### Evidence

- .github/workflows/ci.yml:3-7, 53-71 — committed workflow on push+pull_request runs ruff check ., ruff format --check ., pytest -m 'not live', validate_repo.py
- grep -nE 'continue-on-error|if:\s|\|\| true' .github/workflows/*.yml -> no hit (exit 1); control line matches
- Pipe grep only hits YAML block scalars 'run: |' (publish.yml:30,39); their bodies contain no shell pipes
- grep for commented-out gates (deaktiviert|disabled|TODO|vorerst) in workflows -> no hit
- ruff check . / ruff format --check . cover src, tests, scripts; probes/ excluded with rationale (pyproject.toml:78-83); lint select pinned (pyproject.toml:92-97)
- runtime: pytest -q -rs -> 215 passed, 18 skipped, all skips 'DISCOVER_SWISS_KEY is not set' in test_live.py (credential, not dependency; CI deselects them)

### Gemessen / Geschlossen / Offen

**Gemessen**
- .github/workflows/ci.yml:3-7, 53-71 — committed workflow on push+pull_request runs ruff check ., ruff format --check ., pytest -m 'not live', validate_repo.py
- grep -nE 'continue-on-error|if:\s|\|\| true' .github/workflows/*.yml -> no hit (exit 1); control line matches
- Pipe grep only hits YAML block scalars 'run: |' (publish.yml:30,39); their bodies contain no shell pipes
- grep for commented-out gates (deaktiviert|disabled|TODO|vorerst) in workflows -> no hit
- ruff check . / ruff format --check . cover src, tests, scripts; probes/ excluded with rationale (pyproject.toml:78-83); lint select pinned (pyproject.toml:92-97)
- runtime: pytest -q -rs -> 215 passed, 18 skipped, all skips 'DISCOVER_SWISS_KEY is not set' in test_live.py (credential, not dependency; CI deselects them)

**Geschlossen**
- 7 of 10 criteria met. Pipeline runs everything on push/PR with no silent-failure constructs; gaps are width-scoped copies, a gate that cannot fire pre-release, and undocumented gate counter-tests.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Check, der nicht gelaufen ist, sieht in jeder Zusammenfassung exakt aus wie einer, der bestanden hat. Grüner Haken, keine Meldung, weiter. Das ist keine Nachlässigkeit im Einzelfall, sondern eine Eigenschaft der Werkzeuge: CI-Oberflächen zeigen Fehlschläge, nicht Abwesenheiten.

### Remediation

Add a CI step looping ruff format --check --line-length 88/100/110/120 over the copied scripts (after reformatting them to a width-stable form), make C8 emit INFO 'not checked: no release heading' instead of returning silently, and record gate counter-tests in CONTRIBUTING.

**Disposition:** The copied portfolio scripts (validate_repo.py, check_release_artifacts.py) are format-stable only at line-length 100; shorten the long expressions so they pass at 88-120.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OPS-007

## Finding: OPS-007 — Dokumentierte Befehle laufen auf den Plattformen, die das Repo behauptet

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-007` |
| **PDF-Reference** | Custom (Portfolio-Fundstück mcp-audit-skill#70/#71, 2026-08-02) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Platforms are named nowhere: no Windows/macOS/Linux statement in README/CONTRIBUTING, pyproject has no 'Operating System' classifier, CI matrix is ubuntu-latest only (ci.yml:25)
- Bash-only commands without a PowerShell counterpart while Windows is implicitly supported: README.md:137, 288; README.de.md:135, 289; docs/DEMO.md:13 'export DISCOVER_SWISS_KEY=...'; README.md:143 'DISCOVER_SWISS_MCP_TRANSPORT=streamable-http python -m ...' (env-prefix syntax)
- No paired PowerShell/POSIX blocks

### Expected Behavior

- [ ] Die Plattformen, die das Repo für sich behauptet, sind an **einer** Stelle benannt — nicht aus Testmatrix, Badge und Prosa zusammenzusuchen
- [ ] Jeder dokumentierte Befehl läuft auf jeder dieser Plattformen, oder der Block ist ausdrücklich einer Plattform zugeordnet
- [ ] Keine `&&`/`||`-Verkettung in einem Befehl, der auch für PowerShell gilt — zwei Zeilen kosten nichts und laufen überall
- [ ] Plattformspezifische Blöcke stehen **paarweise** da (PowerShell *und* POSIX), nicht als Fussnote zu einem POSIX-Original
- [ ] Die Suche aus Modus 2 deckt alle Dateien ab, in denen Anleitungen stehen — inklusive der übersetzten Fassungen
- [ ] Die Prüfung ist einmal gegen einen bekannt gebrochenen Befehl gehalten worden

### Evidence

- pyproject.toml:38-41 and tests/test_smoke.py:94-105 — Windows support is claimed implicitly (tzdata for win32, 'Fix start on Windows' commit 160fd7f)
- grep -rnE '^\s*[a-z].*(&&|\|\|)' README*.md CONTRIBUTING*.md docs/*.md -> no hit (exit 1); control 'pip install x && y' matches
- Search covered README.md, README.de.md, CONTRIBUTING.md, docs/*.md (all instruction files, incl. German)

### Gemessen / Geschlossen / Offen

**Gemessen**
- pyproject.toml:38-41 and tests/test_smoke.py:94-105 — Windows support is claimed implicitly (tzdata for win32, 'Fix start on Windows' commit 160fd7f)
- grep -rnE '^\s*[a-z].*(&&|\|\|)' README*.md CONTRIBUTING*.md docs/*.md -> no hit (exit 1); control 'pip install x && y' matches
- Search covered README.md, README.de.md, CONTRIBUTING.md, docs/*.md (all instruction files, incl. German)

**Geschlossen**
- 3 of 6 criteria met (no && chaining, search scope, counter-check done); the implicit Windows claim is not matched by the documented commands.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Sie sind Code. Sie werden von Menschen ausgeführt, meist genau einmal, meist von jemandem, der das Repo noch nicht kennt — und in dem Moment, in dem sie brechen, ist niemand da, der die Ursache erkennt. Anders als Code laufen sie in **keiner** Pipeline. Ein Repo kann eine grüne CI über vier Plattform-Matrix-Felder haben und eine Setup-Anleitung, die auf der Hälfte davon nicht startet.

### Remediation

State supported platforms once in the README and add PowerShell equivalents ($env:DISCOVER_SWISS_KEY = '...'; $env:DISCOVER_SWISS_MCP_TRANSPORT = 'streamable-http') next to each export block in README.md, README.de.md and docs/DEMO.md.

**Disposition:** Name the supported platforms and add PowerShell equivalents for the env-var examples.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OPS-008

## Finding: OPS-008 — Prüflogik in Workflow-Heredocs ist nicht nachweisbar

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-008` |
| **PDF-Reference** | Custom (Portfolio-Fundstück mcp-audit-skill#81, 2026-08-03) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- The two extracted guards that decide red/green have no tests: grep -rl 'validate_repo|check_release_artifacts' tests/ -> no hit
- State set incomplete: validate_repo.py C8 returns silently when CHANGELOG has no release heading (scripts/validate_repo.py:566-576); counter-test with a detuned badge -> exit 0, no warning
- No documented mutation counter-test for the guards

### Expected Behavior

_(siehe Check-Definition)_

### Evidence

- grep -c "<<" .github/workflows/*.yml -> 0 for ci.yml and publish.yml; control "python - <<'PY'" matches -> no heredoc guard in any workflow
- .github/workflows/ci.yml:70-71, publish.yml:38-42 — judging logic lives in scripts/validate_repo.py and scripts/check_release_artifacts.py, called by exit code
- tests/test_server.py:88-95,148-154 — scripts/gen_tool_hashes.py is loaded and exercised by a test

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep -c "<<" .github/workflows/*.yml -> 0 for ci.yml and publish.yml; control "python - <<'PY'" matches -> no heredoc guard in any workflow
- .github/workflows/ci.yml:70-71, publish.yml:38-42 — judging logic lives in scripts/validate_repo.py and scripts/check_release_artifacts.py, called by exit code
- tests/test_server.py:88-95,148-154 — scripts/gen_tool_hashes.py is loaded and exercised by a test

**Geschlossen**
- 2 of 5 criteria met. The core rule (no judging heredocs in workflows) holds, but the extracted guards are untested and one of them collapses 'not checked' into 'OK'.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Prüflogik in einem Workflow-Heredoc — `run: |` gefolgt von `python - <<'PY' … PY` — ist ausführbarer Code an der einzigen Stelle im Repo, an der Code keine Tests haben kann. Er lässt sich nicht importieren, nicht mit Grenzfällen aufrufen, nicht mutationstesten. Er wird genau einmal geschrieben, in dem Moment, in dem der Autor sicher ist, dass er stimmt, und danach nie wieder befragt.

### Remediation

Add tests/test_scripts.py covering validate_repo.py (server.json drift -> ERROR, badge drift, missing release heading -> explicit 'not checked') and check_release_artifacts.py (tag mismatch, missing marker, description > 100), each run once against a deliberately broken input.

**Disposition:** Add tests for validate_repo.py and check_release_artifacts.py; a check that did not run must not report OK.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### OPS-009

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


### OPS-010

## Finding: OPS-010 — Gegenprobe als Abnahmekriterium — auch die Uhr und der Patch

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `OPS-010` |
| **PDF-Reference** | Custom (Katalog-Lücke gegen mcp-transport-hardening-skill Regel 6, 2026-08-07) |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Surviving mutation M1: TOTAL_BUDGET = 25.0 -> 1e9 (client.py:248) — 215 passed. The wall-clock budget has no test at all, under fake or real time
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide (client_module.time is time); the event loop clock reads time.monotonic too
- No test guards the _sleep seam (no assertion that real asyncio.sleep still waits)
- No documentation of which test turns red per central assurance, no dated counter-test record, nothing in CONTRIBUTING.md (grep gegenprobe|mutation|negative control over tests/ and CONTRIBUTING.md -> no hit)

### Expected Behavior

- [ ] Für jede zentrale Zusicherung des Servers ist **dokumentiert**, welcher Test rot wird, wenn man sie bricht
- [ ] Die Gegenprobe ist **gefahren** worden, nicht nur vorgesehen — mit Datum oder Commit, an dem sie lief
- [ ] Mutationen, die **nicht** anschlagen, stehen im Befund; sie sind das Ergebnis, nicht der Ausschuss
- [ ] Jede Zusicherung über **Wanduhrzeit** hat mindestens einen Test unter **echter** Zeit; eine Uhr, die nur beim Schlafen vorrückt, ist dort kein Beleg
- [ ] Kein Test patcht ein **fremdes** Modul global (`modul.asyncio`, `modul.time`, `modul.random`); gepatcht wird eine eigene Naht (`modul._sleep`)
- [ ] Ein Test bewacht diese Naht — er zeigt, dass das echte `asyncio.sleep` nach der Fixture noch wirkt
- [ ] Der Weg, eine Gegenprobe zu fahren, steht im `CONTRIBUTING`; eine Praxis, die nur einer kennt, überlebt den nächsten Beitrag nicht
- [ ] **Gegenprobe zur Gegenprobe:** Es ist einmal gezeigt worden, dass die Mutations-Methode selbst anschlägt — eine Mutation, von der bekannt ist, dass sie einen Test bricht, bricht ihn auch

### Evidence

- src/discover_swiss_mcp/client.py:275-279 — own seam _sleep = asyncio.sleep; tests/conftest.py:75-84 patches client_module._sleep, not asyncio
- Mutation counter-tests run by the auditor on a scratch copy (PYTHONPATH pointed at the copy, verified via module __file__): M0 control RETRY_DELAYS (2,4,8)->(1,4,8): 1 failed (method fires); M2 egress allow-list disabled (net.py 'if False and host not in EGRESS_ALLOWLIST'): 1 failed; M3 POST redirect gate disabled: 1 failed; M4 key rendered in safe_summary: 1 failed
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide; re-read by the report author at bd0e371 (step 4 gate: third observation moved from gaps into evidence)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:275-279 — own seam _sleep = asyncio.sleep; tests/conftest.py:75-84 patches client_module._sleep, not asyncio
- Mutation counter-tests run by the auditor on a scratch copy (PYTHONPATH pointed at the copy, verified via module __file__): M0 control RETRY_DELAYS (2,4,8)->(1,4,8): 1 failed (method fires); M2 egress allow-list disabled (net.py 'if False and host not in EGRESS_ALLOWLIST'): 1 failed; M3 POST redirect gate disabled: 1 failed; M4 key rendered in safe_summary: 1 failed
- tests/test_client.py:385 — monkeypatch.setattr(client_module.time, 'monotonic', ...) patches the stdlib time module process-wide; re-read by the report author at bd0e371 (step 4 gate: third observation moved from gaps into evidence)

**Geschlossen**
- 2 of 8 criteria met (counter-counter-test by the auditor; surviving mutation now on record). The suite does catch egress, redirect and secret regressions, but the wall-clock budget is unguarded and one test patches a foreign module globally.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Test, der grün bleibt, wenn man die Implementierung entfernt, prüft nichts. Er kostet Laufzeit, erzeugt eine Zeile im Report und eine Überzeugung, die durch nichts gedeckt ist — die teuerste Form von Testabdeckung, weil sie den Blick von der Stelle wegzieht, an der nichts steht.

### Remediation

Add a real-time test: respx side_effect sleeping 1 s with TOTAL_BUDGET monkeypatched to 0.05 on the client module, asserting UpstreamUnavailableError within <0.5 s; replace the time.monotonic patch with an own seam (_monotonic = time.monotonic in client.py); add a test that asyncio.sleep(0.05) still takes >=0.04 s under the sleeps fixture; document the counter-test procedure and results in CONTRIBUTING.md.

**Disposition:** Mutation TOTAL_BUDGET 25 -> 1e9 survives all 215 tests. Add a real-time budget test, replace the global time.monotonic patch with an own seam, guard the _sleep seam, document the counter-test procedure in CONTRIBUTING.

### Effort Estimate

M

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `OPS-010` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SCALE-010

## Finding: SCALE-010 — subscriptions/listen statt GET-Endpunkt und resources/subscribe

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SCALE-010` |
| **PDF-Reference** | SEP-2575 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README does not state that the server emits no change notifications (criterion 1 requires one sentence, not silence)
- The SDK's backward-compatible 2025-11-25 session path still serves a server-initiated GET stream: after a legacy initialize, GET /mcp with mcp-session-id → 200 text/event-stream (runtime). Modern GET is 405; the legacy stream is SDK compat behaviour, not server code

### Expected Behavior

- [ ] Führt der Server keine Änderungsbenachrichtigungen, ist das belegt und im README festgehalten — mit einem Satz, nicht durch Schweigen
- [ ] Kein `resources/subscribe` / `resources/unsubscribe` mehr im Code
- [ ] Kein GET-Endpunkt für serverinitiierte Nachrichten; ein GET auf den MCP-Pfad antwortet `405`
- [ ] Führt der Server Benachrichtigungen: Der Client trägt sich über `subscriptions/listen` je Typ ein, und der Server bestätigt
- [ ] Jede Benachrichtigung trägt `io.modelcontextprotocol/subscriptionId`
- [ ] `notifications/progress` und `notifications/message` laufen weiter auf dem Antwortstrom ihres Requests, **nicht** auf `subscriptions/listen` — mit einem Test belegt
- [ ] Der Reverse Proxy puffert den langlebigen Strom nicht und schliesst ihn nicht vor dem Server

### Evidence

- src/ — grep 'resources/(un)?subscribe|subscriptions/listen|subscriptionId|toolsListChanged|notifications/progress|report_progress|ctx\.info|list_changed' → no hit (control fires on 3 control lines)
- runtime (audit): initialize (2025-11-25) response capabilities tools.listChanged=false, prompts.listChanged=false, resources.listChanged=false, resources.subscribe=false
- runtime (audit): resources/subscribe → -32601 Method not found
- runtime (audit): GET /mcp with MCP-Protocol-Version 2026-07-28 → 405, Allow: POST

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/ — grep 'resources/(un)?subscribe|subscriptions/listen|subscriptionId|toolsListChanged|notifications/progress|report_progress|ctx\.info|list_changed' → no hit (control fires on 3 control lines)
- runtime (audit): initialize (2025-11-25) response capabilities tools.listChanged=false, prompts.listChanged=false, resources.listChanged=false, resources.subscribe=false
- runtime (audit): resources/subscribe → -32601 Method not found
- runtime (audit): GET /mcp with MCP-Protocol-Version 2026-07-28 → 405, Allow: POST

**Geschlossen**
- The server has no notification or subscription mechanism (code grep with control, capabilities, Method-not-found) and the modern GET answers 405. The README is silent on notifications and the legacy-era GET stream remains reachable for 2025-11-25 clients → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: **Die Trennlinie, an der die Migration schiefgeht:** Nicht alles, was der Server ungefragt sendet, gehört in diesen Strom. Request-bezogene Benachrichtigungen — `notifications/progress`, `notifications/message` — laufen weiterhin auf dem Antwortstrom **des Requests, zu dem sie gehören**. Nur was keinem Request zugeordnet ist, gehört auf `subscriptions/listen`.

### Remediation

Add one README sentence under the protocol/transport section: 'This server sends no list-changed or resource notifications; tools are static.' Optionally note that legacy (2025-11-25) sessions still get the SDK's GET stream, or disable legacy protocol support if only 2026-07-28 clients are targeted.

**Disposition:** README: one sentence that the server emits no change notifications.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SCALE-010` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SDK-003

## Finding: SDK-003 — Context Injection für Progress Reports und Logging

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SDK-003` |
| **PDF-Reference** | Sec 3.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No ctx.report_progress on paths that can exceed 2 s: list fallback up to FALLBACK_MAX_CALLS sequential calls (tools.py:846-871), retry ladder/429 waits up to 25–55 s (client.py:248,772)
- No test demonstrating that no notifications/message is emitted for a request without logLevel (trivially true today, not held by a test)

### Expected Behavior

- [ ] Tools mit voraussichtlicher Laufzeit > 2s haben `ctx: Context`-Parameter
- [ ] Lang laufende Tools rufen `ctx.report_progress()` mindestens alle 1–2 Sekunden
- [ ] Fehlerfälle, die nicht direkt Tool-Result werden, werden via `ctx.warning()` / `ctx.error()` geloggt (nicht stumm geschluckt)
- [ ] Bei schreibenden Tools (HITL-005): `ctx.elicit()` für Bestätigung verwendet
- [ ] Logger-Statements im Code-Body nutzen `ctx.info()`, nicht direkt `print()` oder Stdlib-`logger` (für stdio-Server kritisch — siehe OBS-004)
- [ ] Auf `2026-07-28`: kein `logging/setLevel`-Handler mehr; der Level kommt aus `io.modelcontextprotocol/logLevel` in `_meta`
- [ ] Auf `2026-07-28`: `notifications/message` wird ausschliesslich für Requests gesendet, die das `logLevel`-Feld trugen — mit einem Test belegt, der einen Request **ohne** das Feld stellt und prüft, dass keine Meldung kommt
- [ ] Auf `2026-07-28`: Der Ausstieg aus dem Logging-Feature hat ein Datum (`ARCH-019`), und der Zielzustand ist `stderr` oder OTel — nicht Stille

### Evidence

- src/discover_swiss_mcp/server.py:231,246,261,276,291,306,321,336 — every tool declares ctx: Context
- src/discover_swiss_mcp/server.py:200-222 — failures logged (log.exception) to stderr and raised as masked ToolError, not swallowed; logging_config.py:32,48 stderr
- grep 'report_progress' src/ → 0; grep 'ctx.(info|warning|error)' src/ → 0 (control: pattern hits .venv/.../mcp/server/mcpserver/context.py)
- runtime: logging/setLevel → -32601 (no handler); server never sends notifications/message (no ctx logging calls)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:231,246,261,276,291,306,321,336 — every tool declares ctx: Context
- src/discover_swiss_mcp/server.py:200-222 — failures logged (log.exception) to stderr and raised as masked ToolError, not swallowed; logging_config.py:32,48 stderr
- grep 'report_progress' src/ → 0; grep 'ctx.(info|warning|error)' src/ → 0 (control: pattern hits .venv/.../mcp/server/mcpserver/context.py)
- runtime: logging/setLevel → -32601 (no handler); server never sends notifications/message (no ctx logging calls)

**Geschlossen**
- Context is injected everywhere and logging correctly targets stderr per the 2026-07-28 baseline; progress reporting for the long fallback/retry paths is missing.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: FastMCP bietet via `Context`-Parameter ein typsicheres Interface zu Server-Internals: Logging, Progress-Reports, Client-Info, Session-State, Sampling, Elicitation. Tools, die `ctx: Context` als Parameter deklarieren, bekommen dieses Objekt automatisch injiziert (Dependency Injection durch FastMCP).

### Remediation

Pass ctx into the fallback scan / retry waits and call await ctx.report_progress(i, total, message) per list page and before each retry sleep.

**Disposition:** ctx.report_progress on the list fallback and on long retry waits.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SDK-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-002

## Finding: SEC-002 — Token Passthrough Prohibition (RFC 8707 Audience Validation)

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-002` |
| **PDF-Reference** | Sec 4.2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No inbound token verification exists at all, so the aud/iss/RFC 8707 criteria (1, 2, 5, 6) are not implemented — the HTTP transport is unauthenticated
- Consequence of the above: any caller that can reach the HTTP port spends the operator's BYOK subscription key (runtime probe: unauthenticated call → upstream request with operator key). Mitigated by the loopback default bind, not by a control
- No user identity propagation (criterion 4) — single-user server, no identity to propagate

### Expected Behavior

- [ ] Token-Verifizierung prüft `aud`-Claim gegen erwarteten Wert
- [ ] Falsche/fehlende Audience → HTTP 401 (nicht 200 mit weiterem Versuch)
- [ ] Upstream-Calls verwenden eigenes Service-Account-Token, nicht Client-Token
- [ ] User-Identität wird via separatem Header (`X-Acting-On-Behalf-Of` o.ä.) propagiert für Audit-Trail
- [ ] `iss`-Claim des **Tokens** wird ebenfalls validiert (Token-Provenienz)
- [ ] Der erwartete `iss` stammt aus einer serverseitig aufgezeichneten Zuordnung, nicht aus dem Token selbst — ein Token, das seinen eigenen Issuer bestimmt, validiert sich selbst
- [ ] Bei `auth_model == "OAuth-Proxy"`: Der `iss`-**Parameter der Authorization-Response** wird nach RFC 9207 geprüft, bevor der Code eingelöst wird — das ist eine andere Prüfung an einer anderen Stelle und steht in `SEC-025`

### Evidence

- src/discover_swiss_mcp/client.py:652-666 — request_headers() builds every upstream header from settings only (Ocp-Apim-Subscription-Key via settings.auth_header, User-Agent, Accept, Accept-Language from the Literal-validated `lang`, categoryVersion); no inbound value is copied
- src/discover_swiss_mcp/config.py:59-61 — auth_header is the single place the server-owned BYOK key is unwrapped; the key comes from DISCOVER_SWISS_KEY (config.py:91), not from any client request
- src/ — grep 'request\.headers|Authorization|headers\.get\(|ctx\.request_context\.request' finds no read of inbound request headers (only net.py:146 reads the upstream response Location header); pattern verified to fire on a control line
- runtime (audit probe, in-process uvicorn on 127.0.0.1:18780 with net.safe_request patched to capture outbound headers): tools/call source_status sent with 'Authorization: Bearer ATTACKER-TOKEN', 'Cookie', 'Mcp-Param-Evil' → HTTP 200; 3 upstream calls captured, header names [accept, accept-language, categoryversion, ocp-apim-subscription-key, user-agent], authorization/cookie absent, ATTACKER nowhere, subscription key == operator key (positive control: the capture does see the real key header)
- runtime: /.well-known/oauth-protected-resource → 404; no inbound auth layer exists on the streamable-http transport

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/client.py:652-666 — request_headers() builds every upstream header from settings only (Ocp-Apim-Subscription-Key via settings.auth_header, User-Agent, Accept, Accept-Language from the Literal-validated `lang`, categoryVersion); no inbound value is copied
- src/discover_swiss_mcp/config.py:59-61 — auth_header is the single place the server-owned BYOK key is unwrapped; the key comes from DISCOVER_SWISS_KEY (config.py:91), not from any client request
- src/ — grep 'request\.headers|Authorization|headers\.get\(|ctx\.request_context\.request' finds no read of inbound request headers (only net.py:146 reads the upstream response Location header); pattern verified to fire on a control line
- runtime (audit probe, in-process uvicorn on 127.0.0.1:18780 with net.safe_request patched to capture outbound headers): tools/call source_status sent with 'Authorization: Bearer ATTACKER-TOKEN', 'Cookie', 'Mcp-Param-Evil' → HTTP 200; 3 upstream calls captured, header names [accept, accept-language, categoryversion, ocp-apim-subscription-key, user-agent], authorization/cookie absent, ATTACKER nowhere, subscription key == operator key (positive control: the capture does see the real key header)
- runtime: /.well-known/oauth-protected-resource → 404; no inbound auth layer exists on the streamable-http transport

**Geschlossen**
- The passthrough prohibition itself is satisfied with positive code and runtime evidence: client tokens never reach discover.swiss; upstream uses the server's own key. The audience/issuer criteria are unmet because the server accepts no inbound token at all. Counted as partial rather than pass because 4 of 7 criteria (aud check, 401 on wrong audience, iss validation, server-side issuer mapping) have no implementation; the practical exposure is bounded by the 127.0.0.1 default.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: «Token Passthrough» bezeichnet das unkritische Weiterreichen eines vom MCP-Client erhaltenen Access-Tokens an einen Upstream-Service (z.B. interne API, Drittanbieter-API). Auf den ersten Blick wirkt das pragmatisch — der Server muss kein eigenes Auth-Konzept implementieren —, ist aber ein Verstoss gegen die OAuth-2.0-Sicherheitsarchitektur.

### Remediation

Document in README/SECURITY.md that the HTTP transport has no inbound authentication and must stay on loopback; if it is ever exposed beyond loopback, add inbound bearer auth (TokenVerifier with aud/iss validation against server-side configured values, 401 on mismatch) before serving tools, and keep the upstream key server-owned as today.

**Disposition:** The HTTP transport has no inbound authentication; client tokens are never forwarded upstream (verified). The server is local-only by design (loopback default). Catalogue question recorded in the audit: auth_model 'API-Key' here means a bring-your-own upstream key, not inbound auth. Accepted together with the SEC-016 fix that refuses a non-loopback bind without explicit opt-in.

### Effort Estimate

M

### Dependencies / Blockers

Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).

### Verification After Fix

- Re-Audit von `SEC-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-003

## Finding: SEC-003 — Progressive Scope-Minimierung: Least-Privilege-Modell

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-003` |
| **PDF-Reference** | Sec 4.3 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No scope hierarchy defined and no per-tool scope requirements
- No per-call scope validation and no 403 + WWW-Authenticate insufficient_scope challenge
- No RFC 9728 Protected Resource Metadata (/.well-known/oauth-protected-resource → 404)
- Only the Origin→403 criterion is met (and only on loopback bind, via SDK default)

### Expected Behavior

- [ ] Scope-Hierarchie ist definiert (kein Omnibus `*:*`)
- [ ] Pro Tool dokumentierte erforderliche Scopes
- [ ] Server validiert Scopes pro Tool-Call (nicht nur beim Login)
- [ ] Bei Insufficient-Scope: HTTP 403 mit `WWW-Authenticate`-Header und konkretem Scope
- [ ] `/.well-known/oauth-protected-resource` wird bedient und nennt Ressourcen-Kennung, Autorisierungsserver und Scopes (RFC 9728, SEP-985)
- [ ] Die dort genannten `scopes_supported` decken sich mit der implementierten Scope-Hierarchie
- [ ] Bei ungültigem Origin antwortet der Transport `403`, nicht `400` (Spec 2025-11-25, Minor #3) — siehe `SEC-024`
- [ ] Initial-Login-Scope ist minimal (Discovery + Public-Read)
- [ ] Granularität: lese/schreibe + Datenklasse als separate Dimensionen
- [ ] Admin-Scopes sind explizit, nicht in Standard-Hierarchie eingebettet

### Evidence

- src/ — grep 'audience|aud|WWW-Authenticate|insufficient_scope|scope|oauth|jwt|Bearer|TokenVerifier|AuthSettings' finds only unrelated uses of the word 'scope' (tools.py:491 geographic scope, server.py:83-84 CacheHint scope='public'); no scope model, no per-tool scope check
- runtime: GET /.well-known/oauth-protected-resource and /.well-known/oauth-protected-resource/mcp → 404 (control: GET /mcp on same server → 405, server was up)
- runtime: POST /mcp with foreign Origin on loopback bind → HTTP 403 'Invalid Origin header' (criterion 7 met via SDK default)
- src/discover_swiss_mcp/server.py:170-175 — all 8 tools annotated readOnlyHint=True, destructiveHint=False (single read-only capability class)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/ — grep 'audience|aud|WWW-Authenticate|insufficient_scope|scope|oauth|jwt|Bearer|TokenVerifier|AuthSettings' finds only unrelated uses of the word 'scope' (tools.py:491 geographic scope, server.py:83-84 CacheHint scope='public'); no scope model, no per-tool scope check
- runtime: GET /.well-known/oauth-protected-resource and /.well-known/oauth-protected-resource/mcp → 404 (control: GET /mcp on same server → 405, server was up)
- runtime: POST /mcp with foreign Origin on loopback bind → HTTP 403 'Invalid Origin header' (criterion 7 met via SDK default)
- src/discover_swiss_mcp/server.py:170-175 — all 8 tools annotated readOnlyHint=True, destructiveHint=False (single read-only capability class)

**Geschlossen**
- auth_model is API-Key (BYOK upstream key) and the HTTP transport has no inbound OAuth at all, so none of the scope criteria is implemented. Measured strictly against the pass criteria this is a fail (1 of ~10 met). Practical risk is low: all tools are read-only over public open data and the transport binds loopback by default; the catalogue's applies_when (auth_model != none) maps a BYOK upstream key onto an inbound-OAuth check — worth a catalogue/profile review.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: OAuth-Scope-Design hat zwei Failure-Modes:

### Remediation

Either (a) record in README/SECURITY.md that the server has no inbound authorization and therefore a single implicit read-only scope, and keep HTTP loopback-only; or (b) if the HTTP transport is to be exposed, add OAuth resource-server support with a minimal read scope (e.g. data:read:public), per-tool scope checks returning 403 + WWW-Authenticate, and /.well-known/oauth-protected-resource.

**Disposition:** No OAuth scopes: there is no inbound OAuth. Same reasoning and same condition as SEC-002.

### Effort Estimate

L

### Dependencies / Blockers

Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).

### Verification After Fix

- Re-Audit von `SEC-003` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-004

## Finding: SEC-004 — SSRF-Prevention: HTTPS-Enforcement + IP-Blocklisting

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-004` |
| **PDF-Reference** | Sec 4.4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- IPv4-mapped IPv6 answers bypass the blocklist: ::ffff:169.254.169.254 and ::ffff:127.0.0.1 are not blocked (ipaddress compares across versions as not-contained). Exploitation requires control of DNS for api.discover.swiss because the host allow-list (net.py:34, 95) restricts targets first — compensated, not closed
- Unspecified (::), multicast (224.0.0.0/4), benchmark (198.18.0.0/15), reserved (240.0.0.0/4) and NAT64 (64:ff9b::/96) ranges not blocked
- No egress proxy (criterion 5) — not applicable in practice: server is local-only, not production/cloud deployed

### Expected Behavior

- [ ] HTTPS-Schema wird vor jedem ausgehenden Request validiert
- [ ] Resolved IP wird gegen Blocklist (private + link-local + loopback) geprüft
- [ ] Cloud-Metadata-IP `169.254.169.254` ist explizit blockiert
- [ ] IPv6-Loopback (`::1`) und IPv6-Link-local (`fe80::/10`) sind blockiert
- [ ] In Production: Egress-Proxy (Smokescreen o.ä.) als Defense-in-Depth

**Nicht hier bewertet: DNS-Pinning.** Ob die geprüfte IP auch die benutzte IP ist, prüft `SEC-005`. Das Pass-Pattern oben löst bereits einmal auf und verwendet die IP — echter Code macht beides in derselben Funktion —, aber das **Kriterium** gehört dorthin, nicht hierher.

Der Grund ist `SKILL.md` §2.5: Zwei Checks, die einander überlappen, doppeln das Finding, und wenn der Server die Ursache behebt, bleibt der zweite rot — der Fix sieht aus, als hätte er nicht gewirkt. Bis v1.3.1 stand «DNS-Resolution erfolgt einmal» wortgleich in beiden Checks.

Zusammengelegt wurden sie trotzdem nicht: Blocklisting und Pinning sind **getrennt behebbar**, und §2.5 verlangt, dass ein Check in *einem* Schritt behebbar bleibt. Ein Server kann die Blockliste korrekt führen und trotzdem zweimal auflösen — das sind zwei Befunde mit zwei Remediationen, nicht einer.

### Evidence

- src/discover_swiss_mcp/net.py:93-94 — scheme != 'https' raises EgressError before any request (test: tests/test_net.py:17-19)
- src/discover_swiss_mcp/net.py:96-103 — host resolved once, every resolved IP checked against BLOCKED_NETWORKS before the request
- src/discover_swiss_mcp/net.py:39-53 — blocklist: 0.0.0.0/8, 10/8, 100.64/10, 127/8, 169.254/16 (covers 169.254.169.254), 172.16/12, 192.168/16, ::1/128, fc00::/7, fe80::/10
- src/discover_swiss_mcp/net.py:133-134 — safe_request re-runs the full check on every redirect hop; tests/test_net.py:75-87 (redirect off allow-list stopped)
- tests/test_net.py:22-35 — parametrized block test for 127.0.0.1, 10.0.0.5, 192.168.1.1, 169.254.169.254, ::1 (215 offline tests pass)
- runtime (audit): net._is_blocked_ip → 169.254.169.254 True, ::1 True, fe80::1 True, fd00::1 True (controls), but ::ffff:169.254.169.254 False, ::ffff:127.0.0.1 False, '::' False, 224.0.0.1 False, 198.18.0.1 False, 64:ff9b::a9fe:a9fe False

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:93-94 — scheme != 'https' raises EgressError before any request (test: tests/test_net.py:17-19)
- src/discover_swiss_mcp/net.py:96-103 — host resolved once, every resolved IP checked against BLOCKED_NETWORKS before the request
- src/discover_swiss_mcp/net.py:39-53 — blocklist: 0.0.0.0/8, 10/8, 100.64/10, 127/8, 169.254/16 (covers 169.254.169.254), 172.16/12, 192.168/16, ::1/128, fc00::/7, fe80::/10
- src/discover_swiss_mcp/net.py:133-134 — safe_request re-runs the full check on every redirect hop; tests/test_net.py:75-87 (redirect off allow-list stopped)
- tests/test_net.py:22-35 — parametrized block test for 127.0.0.1, 10.0.0.5, 192.168.1.1, 169.254.169.254, ::1 (215 offline tests pass)
- runtime (audit): net._is_blocked_ip → 169.254.169.254 True, ::1 True, fe80::1 True, fd00::1 True (controls), but ::ffff:169.254.169.254 False, ::ffff:127.0.0.1 False, '::' False, 224.0.0.1 False, 198.18.0.1 False, 64:ff9b::a9fe:a9fe False

**Geschlossen**
- HTTPS enforcement, post-resolution IP check, metadata and IPv6 loopback/link-local blocking are all present with tests. The blocklist is range-based on the raw address and misses IPv4-mapped IPv6 forms of the blocked ranges — the 'IPv6-mapped' trick named in the check. Because the host allow-list admits only api.discover.swiss, the gap is not reachable via tool arguments, so it is rated below critical; still a gap in criterion 2/3 → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Server-Side Request Forgery (SSRF) entsteht, wenn ein MCP-Server URLs aus User-Input (oder LLM-generierten Args) direkt an HTTP-Clients weitergibt. Ein Angreifer kann den Server dann zwingen, beliebige interne Adressen abzurufen — insbesondere die Cloud-Metadata-Endpunkte.

### Remediation

In _is_blocked_ip: unwrap ip.ipv4_mapped (and ip.sixtofour / NAT64 if desired) before the range check, and additionally reject ip.is_private, is_loopback, is_link_local, is_multicast, is_reserved, is_unspecified; add ::ffff:169.254.169.254 and ::ffff:127.0.0.1 to the parametrized test in tests/test_net.py.

**Disposition:** IPv4-mapped IPv6 addresses bypass the blocklist (::ffff:169.254.169.254, ::ffff:127.0.0.1 verified). Unwrap ipv4_mapped before the check; add tests.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-006

## Finding: SEC-006 — Lokaler Server: stdio-Transport zwingend (Netzwerk-Isolation)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-006` |
| **PDF-Reference** | Sec 4.5 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- README has no Claude Desktop / mcpServers configuration example for the local stdio use-case (criterion 3 only partly met)
- README has no separate cloud-deployment section with security notes (criterion 4 unmet); the only network note is SECURITY.md:39-41, which references a host allow-list the code does not provide (see SEC-024)

### Expected Behavior

- [ ] Default-Transport (ohne ENV-Var) ist `stdio`
- [ ] SSE/HTTP-Transport nur via expliziter `MCP_TRANSPORT`-ENV-Var aktivierbar
- [ ] README dokumentiert lokalen Use-Case primär (stdio + Claude Desktop)
- [ ] README dokumentiert Cloud-Use-Case separat mit Sicherheitshinweisen
- [ ] Default-Start öffnet keinen TCP-Port (Runtime-Test)

### Evidence

- src/discover_swiss_mcp/config.py:48 — Settings.transport default 'stdio'; config.py:105-106 — DISCOVER_SWISS_MCP_TRANSPORT defaults to 'stdio', anything other than stdio/streamable-http is a ConfigError
- src/discover_swiss_mcp/server.py:358-370 — HTTP (uvicorn) only when settings.transport == 'streamable-http', else mcp.run() (stdio)
- runtime (audit): `python -m discover_swiss_mcp` without transport env → 0 listening TCP sockets for the PID (/proc/<pid>/fd × /proc/net/tcp state 0A); control: same check on a streamable-http run → 1 listening socket
- README.md:139-143 — stdio shown first ('stdio (Claude Desktop and other local clients)'), HTTP shown as explicit opt-in with 'binds to 127.0.0.1:8000 by default (localhost only)'
- README.md:111 — 'Dual transport — stdio (Claude Desktop) and Streamable HTTP (cloud)'

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:48 — Settings.transport default 'stdio'; config.py:105-106 — DISCOVER_SWISS_MCP_TRANSPORT defaults to 'stdio', anything other than stdio/streamable-http is a ConfigError
- src/discover_swiss_mcp/server.py:358-370 — HTTP (uvicorn) only when settings.transport == 'streamable-http', else mcp.run() (stdio)
- runtime (audit): `python -m discover_swiss_mcp` without transport env → 0 listening TCP sockets for the PID (/proc/<pid>/fd × /proc/net/tcp state 0A); control: same check on a streamable-http run → 1 listening socket
- README.md:139-143 — stdio shown first ('stdio (Claude Desktop and other local clients)'), HTTP shown as explicit opt-in with 'binds to 127.0.0.1:8000 by default (localhost only)'
- README.md:111 — 'Dual transport — stdio (Claude Desktop) and Streamable HTTP (cloud)'

**Geschlossen**
- Code-side criteria (stdio default, HTTP only via explicit env var, no port on default start — runtime verified with control) are met. The two documentation criteria are only partly met: local use is shown as a bare command, and HTTP is labelled '(cloud)' without any cloud section or security guidance.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Lokale MCP-Server laufen mit den Privilegien des Users — sie haben Zugriff auf das Filesystem, Netzwerk-Interfaces, Subprozess-Spawning, Environment-Variablen, gespeicherte SSH-Keys, Browser-Cookies. Ein lokaler Server, der gleichzeitig auf einem Netzwerk-Port lauscht, weitet diese User-Privilegien auf jede Entity aus, die diesen Port erreichen kann.

### Remediation

Add to README a 'Local use (Claude Desktop)' block with the full mcpServers JSON (command, args, env DISCOVER_SWISS_KEY) and a separate 'HTTP transport' section stating it is for loopback/local testing unless fronted by auth and a host allow-list, with the security caveats.

**Disposition:** README: Claude Desktop configuration example for stdio.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-006` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-007

## Finding: SEC-007 — Container-Sandboxing: Docker / chroot mit minimalen Privilegien

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-007` |
| **PDF-Reference** | Sec 4.5 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No container image or sandbox of any kind: no non-root USER, no read-only root FS, no dropped capabilities, no seccomp profile (criteria 1-5 unmet)
- Server runs as the local user with access to that user's files and environment (including DISCOVER_SWISS_KEY and any other secrets in the MCP host's env)

### Expected Behavior

- [ ] Dockerfile setzt `USER` mit nicht-root UID (≥ 10000)
- [ ] Bei Kubernetes: `runAsNonRoot: true`, `runAsUser` explizit, `allowPrivilegeEscalation: false`
- [ ] Bei Kubernetes: `readOnlyRootFilesystem: true` mit `tmpfs`-Volume für `/tmp`
- [ ] Bei Kubernetes: `capabilities.drop: ["ALL"]`
- [ ] seccomp-Profile mindestens `RuntimeDefault`
- [ ] Bei File-Tools: Volume-Mounts nur für erlaubte Pfade, ggf. read-only

### Evidence

- repo — `find` for Dockerfile*, *compose*.y*ml, railway.toml, render.yaml, k8s/, helm/ (excluding .venv) returns nothing; control: same find expression matches ./pyproject.toml; `git ls-files | grep -iE 'docker|compose|k8s|helm|railway|render'` → no match (91 tracked files)
- README.md:127-143 — only documented run mode is pip install -e + `python -m discover_swiss_mcp` directly on the host, with user privileges
- src/ — no file-system tools (grep 'open\(|Path\(' in src/ → no file access), so criterion 6 is not applicable

### Gemessen / Geschlossen / Offen

**Gemessen**
- repo — `find` for Dockerfile*, *compose*.y*ml, railway.toml, render.yaml, k8s/, helm/ (excluding .venv) returns nothing; control: same find expression matches ./pyproject.toml; `git ls-files | grep -iE 'docker|compose|k8s|helm|railway|render'` → no match (91 tracked files)
- README.md:127-143 — only documented run mode is pip install -e + `python -m discover_swiss_mcp` directly on the host, with user privileges
- src/ — no file-system tools (grep 'open\(|Path\(' in src/ → no file access), so criterion 6 is not applicable

**Geschlossen**
- The check applies to local-stdio deployments. The server ships no sandboxing mechanism and documents none; all applicable criteria are unmet. Risk is moderated by a small dependency set and read-only, no-filesystem tool code, but that is not a sandbox.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Lokale stdio-Server (siehe SEC-006) eliminieren die Netzwerk-Angriffsfläche, behalten aber das Risiko, dass ein kompromittierter Server-Code (durch Supply-Chain-Attack, böswilliges Update, oder Bug-Exploitation) mit User-Privilegien ausgeführt wird. Read-Zugriff auf `~/.ssh/`, `~/.aws/credentials`, Browser-Cookies, lokal gespeicherte Tokens — alles direkt erreichbar.

### Remediation

Ship a Dockerfile (python slim, non-root USER 10001, no secrets in layers) and document a stdio launch via `docker run -i --rm --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges -e DISCOVER_SWISS_KEY ghcr.io/.../discover-swiss-mcp` in the Claude Desktop config; alternatively document uvx-based isolation as the minimum and mark container use as recommended.

**Disposition:** No container is shipped; the server runs as a local stdio process of the user. If a container image is ever published, it gets non-root, read-only FS and dropped capabilities in the same PR.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-013

## Finding: SEC-013 — API-Key-Storage: Secret Manager statt Plain-Text Env-Vars

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-013` |
| **PDF-Reference** | Sec 4 (Empirie 2025) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No secret-access audit (criterion 6): no secret manager and no log event for key use
- Stufe-1 choice is documented in SECURITY.md but without the explicit justification the check asks for (data class Public Open Data, BYOK, local deployment) and not in a secret-management document
- No reload mechanism without restart (TTL cache/reload); rotation requires a process restart — acceptable for local stdio but not what criterion 5 names

### Expected Behavior

- [ ] Bei `Verwaltungsdaten`/`PII`: Stufe 3 (Secret Manager) oder 4 (Workload Identity)
- [ ] Bei `Public Open Data`: Stufe 1 ist akzeptabel, aber dokumentiert in `docs/secret-management.md`
- [ ] Container-Image enthält keine Secrets im Layer (`docker history`-Test bestanden)
- [ ] Secret-Manager-Region ist Schweiz/EU (DSG, siehe CH-001)
- [ ] Rotation ist möglich ohne Code-Änderung (TTL-Cache oder Reload-Mechanismus)
- [ ] Secret-Access wird auditiert (Secret-Manager-eigenes Audit-Log oder OBS-005)

### Evidence

- src/discover_swiss_mcp/config.py:45 — api_key held as pydantic SecretStr; config.py:59-61 — auth_header is the only unwrap; config.py:75 — safe_summary logs only 'set'/'missing'
- src/discover_swiss_mcp/config.py:91 — key read from env var DISCOVER_SWISS_KEY only (Stufe 1, plain env var); no file-based config
- tests/test_smoke.py:60-68 — asserts key absent from repr/str/model_dump_json/repr(client) and present only in the outbound header
- SECURITY.md:12-25 — documents env-only storage, SecretStr masking, .gitignore coverage and 'rotate first' if pushed
- .gitignore — ignores .env, .env.*, *.key, *.pem, credentials.json, secrets.yaml, config.local.*
- src/discover_swiss_mcp/server.py:117-118 — settings loaded once per process in the lifespan; rotation = change env + restart, no code change

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:45 — api_key held as pydantic SecretStr; config.py:59-61 — auth_header is the only unwrap; config.py:75 — safe_summary logs only 'set'/'missing'
- src/discover_swiss_mcp/config.py:91 — key read from env var DISCOVER_SWISS_KEY only (Stufe 1, plain env var); no file-based config
- tests/test_smoke.py:60-68 — asserts key absent from repr/str/model_dump_json/repr(client) and present only in the outbound header
- SECURITY.md:12-25 — documents env-only storage, SecretStr masking, .gitignore coverage and 'rotate first' if pushed
- .gitignore — ignores .env, .env.*, *.key, *.pem, credentials.json, secrets.yaml, config.local.*
- src/discover_swiss_mcp/server.py:117-118 — settings loaded once per process in the lifespan; rotation = change env + restart, no code change

**Geschlossen**
- Data class is Public Open Data and deployment is local-only, so plain env var (Stufe 1) is acceptable provided it is documented. Key handling in code is exemplary (SecretStr, single unwrap, test). Container and region criteria are not applicable (no image, no secret manager). Audit trail is absent and the Stufe-1 rationale is implicit → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: ARCH-005 verlangt: **keine Hardcoded Secrets im Code**. SEC-013 geht weiter: in Production reichen Plain-Text Env-Vars nicht aus. Empirisch werden 53% der OSS-MCP-Server mit langlebigen Static API Keys betrieben — die in `.env`-Dateien, Container-Images, CI-Logs, und Container-Filesystem-Dumps geleakt werden.

### Remediation

Add a short 'Secret management' section (README or docs/secret-management.md) stating Stufe 1 is used deliberately because the key is a personal BYOK key for public open data on a local process, how to rotate (portal → env → restart), and that a secret manager is required if the server is ever deployed shared/cloud.

**Disposition:** Key in an environment variable, held as SecretStr, never logged (tested). No secret manager for a local bring-your-own-key tool; the reason goes into SECURITY.md.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-013` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-016

## Finding: SEC-016 — 0.0.0.0-Binding-Prevention (NeighborJack)

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-016` |
| **PDF-Reference** | Sec 4 (Empirie 2025) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Non-loopback bind is silent: the 0.0.0.0 run logged no warning (only the lifespan INFO event carrying host=0.0.0.0), and there is no host allow-list to compensate (criterion 7 unmet)
- README does not explain the local vs container differentiation or warn against 0.0.0.0 outside containers (criterion 6 unmet)
- No deployment configuration exists in which an explicit 0.0.0.0 would live (criterion 5 not demonstrable; server is local-only)

### Expected Behavior

- [ ] Im Code ist **kein** `0.0.0.0`-Binding als Default hardcoded
- [ ] Die Bind-Adresse ist **konfigurierbar** — Environment-Variable *oder* CLI-Flag; der Mechanismus ist frei
- [ ] Der Default ist **Loopback** (`127.0.0.1`)
- [ ] Der gesetzte Wert **erreicht den Listener**: er wird an *jeden* Pfad durchgereicht, der die App oder den Server baut, und ein Lauf mit gesetztem Wert zeigt ihn im Startlog (Modus 3)
- [ ] `0.0.0.0` steht **explizit in der Deployment-Konfiguration** — Dockerfile, `railway.toml`, Compose-File oder Start-Kommando —, nicht im Code
- [ ] README erklärt die Differenzierung lokal/container
- [ ] Ein Bind ausserhalb Loopback ist **nicht still**: Wenn keine eingehende Host-Allow-List ihn kompensiert, sagt eine Startwarnung, dass der Server jetzt im Netz steht

### Warum die Kriterien die Eigenschaft nennen und nicht den Mechanismus

Bis v1.4.x verlangte Kriterium 2 wörtlich «via **Environment-Variable**». Das misst die Bauform statt der Sache. `zurich-opendata-mcp` löst dieselbe Aufgabe mit `--host` und Default `127.0.0.1` — Absicht vollständig erfüllt, Kriterium wörtlich verfehlt. Ein Check, der so gelesen wird, erzeugt ein Finding gegen eine korrekte Implementierung und lädt zur Gegenrichtung ein: eine `MCP_HOST`-Variable nachzurüsten, die niemand liest, damit die Zeile grün wird.

**Der Mechanismus ist nicht der Punkt — das Durchreichen ist es.** Vor `0.7.0` hatte derselbe Server gar keine Konfigurationsfläche: `mcp.run(transport="streamable-http", port=…)` ohne `host=`, uvicorn band immer `127.0.0.1`, und es gab kein Flag, das daran etwas geändert hätte. Ein Kriterium der Form «es existiert eine Env-Var» hätte diesen Zustand angezeigt, aber den Folgefehler nicht: dass eine vorhandene Option den Listener nicht erreicht. Deshalb steht die Wirkung im Kriterium und wird in Modus 3 gemessen, nicht die Herkunft des Wertes.

### Abgrenzung der Startwarnung gegen `SEC-024`

Kriterium 7 war bis v1.4.x als «Optional» geführt. Es ist keines: Alle drei Portfolio-Server, aus denen die Belege stammen, warnen beim Nicht-Loopback-Bind. Was sie **nicht** tun, ist die Container-Detection, die hier früher als Auslöser stand — die ist in keinem einzigen implementiert. Ausgelöst wird bei allen dreien durch die **fehlende Allow-List**, und deshalb ist das Kriterium so formuliert.

Damit kann **dieselbe Logzeile** zwei Checks bedienen, und die Frage, ob das eine Doppelung ist, gehört beantwortet: Nein, aber knapp. `SEC-024` fragt, ob die *Abwesenheit der Allow-List* angesagt wird — Subjekt ist die Allow-List. Hier ist das Subjekt die **Exposition**: dass der Server das Loopback verlassen hat. Zwei Server können deshalb hier bestehen und dort durchfallen (`0.0.0.0` mit Allow-List, kein Wort im Log) und umgekehrt. Wer die Zeile entfernt, verletzt beide — das ist kein Doppelbefund, sondern eine Ursache mit zwei Wirkungen.

Der vollere Fall ist trotzdem besser und in `bag-health-mcp` gebaut: Warnung ohne Allow-List, `INFO` **mit** Allow-List. Dann ist der Bind nie still, auch nicht im sauber konfigurierten Deployment. Gefordert ist er nicht — wer die Allow-List setzt, hat die Exposition erkennbar entschieden.

### Evidence

- src/discover_swiss_mcp/config.py:49 — Settings.host default '127.0.0.1'; config.py:129 — DISCOVER_SWISS_MCP_HOST env var, default '127.0.0.1'
- src/discover_swiss_mcp/server.py:364-368 — settings.host passed both to mcp.streamable_http_app(host=…) and to uvicorn.run(host=…); the only network path
- repo — grep for 0.0.0.0 host defaults in src/ and config files finds none (only net.py:42 '0.0.0.0/8' in the egress blocklist)
- runtime (audit): default run → 'Uvicorn running on http://127.0.0.1:18766'; with DISCOVER_SWISS_MCP_HOST=0.0.0.0 → 'Uvicorn running on http://0.0.0.0:18767' (value reaches the listener)
- README.md:142 and README.md:247 — default bind 127.0.0.1 documented, DISCOVER_SWISS_MCP_HOST listed

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:49 — Settings.host default '127.0.0.1'; config.py:129 — DISCOVER_SWISS_MCP_HOST env var, default '127.0.0.1'
- src/discover_swiss_mcp/server.py:364-368 — settings.host passed both to mcp.streamable_http_app(host=…) and to uvicorn.run(host=…); the only network path
- repo — grep for 0.0.0.0 host defaults in src/ and config files finds none (only net.py:42 '0.0.0.0/8' in the egress blocklist)
- runtime (audit): default run → 'Uvicorn running on http://127.0.0.1:18766'; with DISCOVER_SWISS_MCP_HOST=0.0.0.0 → 'Uvicorn running on http://0.0.0.0:18767' (value reaches the listener)
- README.md:142 and README.md:247 — default bind 127.0.0.1 documented, DISCOVER_SWISS_MCP_HOST listed

**Geschlossen**
- Loopback default, configurable bind and propagation to both the app builder and the listener are verified by two start-log runs. The silent non-loopback bind is the substantive gap; combined with SEC-024 a 0.0.0.0 bind exposes an unauthenticated, host-unchecked endpoint without any log signal. Not critical because it requires an explicit operator opt-in.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die empirische Untersuchung von 2025 ergab: ein erheblicher Teil der OSS-MCP-Server bindet ihren HTTP-Listener an `0.0.0.0` (alle Interfaces) und vertraut implizit darauf, dass Firewall-Regeln den Zugang beschränken. Auf einem Entwickler-Laptop in einem öffentlichen WLAN, einem Co-Working-Space oder einer Konferenz wird der lokale MCP-Server damit für **alle** Geräte im selben Subnetz erreichbar.

### Remediation

In main(): if settings.host not in ('127.0.0.1','localhost','::1') and no host allow-list is configured, log a WARNING naming the exposure; add a README 'Network binding' paragraph (loopback default; 0.0.0.0 only in containers, together with an allow-list).

**Disposition:** A 0.0.0.0 bind is silent. Refuse a non-loopback bind unless DISCOVER_SWISS_MCP_ALLOW_REMOTE=1 is set, and log a warning when it is.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-016` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-018

## Finding: SEC-018 — Input-Validation an Tool-Boundaries (Pydantic strict / Zod)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-018` |
| **PDF-Reference** | Sec 3 / Sec 4 (Defense-in-Depth) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- strict=True is not set on any input model: page='5' is coerced to 5 (runtime)
- String fields have max_length but no whitelist pattern at the schema boundary; query and identifier accept control characters/NUL (runtime: 'test\x00\r\ninject' accepted by SearchInput); identifier is only regex-checked later in client.get_vertex
- List item strings (types, amenities, facets) have no per-item length/pattern: a 10'000-char types entry is accepted
- No parametrized edge-case tests for too-long strings, unknown fields or control characters (existing tests cover page_size>50, radius without near, missing scope)

### Expected Behavior

- [ ] **Alle** Tool-Argumente haben Schema-Validation (Pydantic / Zod / vergleichbar)
- [ ] Numerische Felder haben `ge`/`le`-Constraints (kein unbegrenzter Range)
- [ ] String-Felder haben `min_length`/`max_length` und idealerweise `pattern`
- [ ] Pattern sind Whitelist-basiert, nicht Blacklist
- [ ] Bei Pydantic: `strict=True` und `extra="forbid"` explizit gesetzt
- [ ] Validation-Errors landen als `isError` im Tool-Result, nicht als Server-Crash (siehe OBS-001)
- [ ] Tests decken Edge-Cases ab: zu lange Strings, Out-of-Range-Numbers, unbekannte Felder

### Evidence

- src/discover_swiss_mcp/tools.py:260-269 — _PagedInput: extra='forbid', page ge=1 le=1000, page_size ge=1 le=MAX_PAGE_SIZE(50), lang Literal
- src/discover_swiss_mcp/tools.py:278-330 — SearchInput: query max_length=200, types max_length=20 items, radius_km gt=0 le=200, locality max_length=100, match Literal; model_validator for radius/near
- src/discover_swiss_mcp/tools.py:333-344 — GetDetailsInput extra='forbid', identifier min_length=1 max_length=128; client.py:226,879-880 — whitelist regex ^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$ applied before the upstream call, client.py:889 quote(safe='')
- src/discover_swiss_mcp/tools.py:250-257 — GeoPoint lat/lon ranges, extra='forbid'; tools.py:2106-2143 ExploreAreaInput facets min_length=1 max_length=12
- runtime (audit, HTTP transport): tools/call get_details with {params:{}} → HTTP 200, result isError=true with validation message (no crash, no upstream call); tests/test_server.py:191-196 asserts invalid input is rejected before any upstream call
- runtime (audit, direct model): extra field → extra_forbidden; query 201 chars → string_too_long; page 1001 → less_than_equal

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:260-269 — _PagedInput: extra='forbid', page ge=1 le=1000, page_size ge=1 le=MAX_PAGE_SIZE(50), lang Literal
- src/discover_swiss_mcp/tools.py:278-330 — SearchInput: query max_length=200, types max_length=20 items, radius_km gt=0 le=200, locality max_length=100, match Literal; model_validator for radius/near
- src/discover_swiss_mcp/tools.py:333-344 — GetDetailsInput extra='forbid', identifier min_length=1 max_length=128; client.py:226,879-880 — whitelist regex ^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$ applied before the upstream call, client.py:889 quote(safe='')
- src/discover_swiss_mcp/tools.py:250-257 — GeoPoint lat/lon ranges, extra='forbid'; tools.py:2106-2143 ExploreAreaInput facets min_length=1 max_length=12
- runtime (audit, HTTP transport): tools/call get_details with {params:{}} → HTTP 200, result isError=true with validation message (no crash, no upstream call); tests/test_server.py:191-196 asserts invalid input is rejected before any upstream call
- runtime (audit, direct model): extra field → extra_forbidden; query 201 chars → string_too_long; page 1001 → less_than_equal

**Geschlossen**
- All tools take Pydantic models with extra='forbid' and numeric bounds; validation errors surface as isError. Missing strict mode, schema-level patterns and per-item constraints, plus thin edge-case tests, leave 3 of 7 criteria unmet → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Tool-Argumente kommen vom LLM — einer probabilistischen Quelle, die halluzinieren, formattieren-falsch oder von Prompt-Injection beeinflusst sein kann. Ohne strikte Input-Validation am Tool-Boundary werden invalide oder bösartige Inputs in die Geschäftslogik weitergereicht und können dort:

### Remediation

Set model_config strict=True (keep str_strip_whitespace, extra='forbid') on all input models; add Annotated[str, StringConstraints(max_length=…, pattern=…)] for query/locality/region (reject C0 control chars), move the identifier regex into GetDetailsInput, and constrain list items (e.g. list[Annotated[str, StringConstraints(max_length=64, pattern=r'^[A-Za-z/]+$')]]); add a parametrized test for too-long, extra-field, control-char and coerced-type inputs.

**Disposition:** strict=True on input models and a control-character check on free-text inputs.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-018` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-021

## Finding: SEC-021 — Egress-Allow-List: Code-Layer und Network-Layer

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-021` |
| **PDF-Reference** | Anhang B5 + B12 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No network-layer egress control (criterion 2) — none exists for the local process and none is documented as out of scope
- Allow-listed host is not documented in README or docs (criterion 3); only the net.py docstring states it
- No documented update procedure for allow-list changes (criterion 5)

### Expected Behavior

- [ ] Code-Layer Allow-List als `frozenset` im Code (nicht config-mutierbar)
- [ ] Network-Layer Egress Control via NetworkPolicy / Security Group / Cloudflare WARP
- [ ] Allow-List-Hosts dokumentiert in `docs/network-egress.md` oder README
- [ ] Pre-Request-Check (`assert_host_allowed`) wird vor jedem ausgehenden Request aufgerufen
- [ ] Update-Verfahren für Allow-List-Erweiterungen dokumentiert
- [ ] DNS-Resolution-Path im Network-Layer explizit erlaubt (sonst Hostname-Lookup bricht)

### Evidence

- src/discover_swiss_mcp/net.py:34 — EGRESS_ALLOWLIST: frozenset[str] = frozenset({'api.discover.swiss'}) (immutable, not env-derived)
- src/discover_swiss_mcp/net.py:67-72,95 — assert_host_allowed called inside assert_url_allowed; net.py:133-134 — runs before every outbound request and on every redirect hop; client.py:717 — the only outbound call site uses net.safe_request
- tests/test_net.py:12-14 (non-allow-listed host rejected), tests/test_net.py:75-87 (redirect to evil.example stopped)
- src/discover_swiss_mcp/config.py:127 — DISCOVER_SWISS_BASE_URL is configurable, but a different host still fails the frozenset check (net.py:95)
- repo — no NetworkPolicy/SecurityGroup/compose/egress config (find + git ls-files, control fires on pyproject.toml); grep 'allow-list|allowlist|api\.discover\.swiss|egress' in README.md/README.de.md/docs/*.md/CHANGELOG.md → no documentation of the egress allow-list (only SECURITY.md:40, which is about the inbound host list)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:34 — EGRESS_ALLOWLIST: frozenset[str] = frozenset({'api.discover.swiss'}) (immutable, not env-derived)
- src/discover_swiss_mcp/net.py:67-72,95 — assert_host_allowed called inside assert_url_allowed; net.py:133-134 — runs before every outbound request and on every redirect hop; client.py:717 — the only outbound call site uses net.safe_request
- tests/test_net.py:12-14 (non-allow-listed host rejected), tests/test_net.py:75-87 (redirect to evil.example stopped)
- src/discover_swiss_mcp/config.py:127 — DISCOVER_SWISS_BASE_URL is configurable, but a different host still fails the frozenset check (net.py:95)
- repo — no NetworkPolicy/SecurityGroup/compose/egress config (find + git ls-files, control fires on pyproject.toml); grep 'allow-list|allowlist|api\.discover\.swiss|egress' in README.md/README.de.md/docs/*.md/CHANGELOG.md → no documentation of the egress allow-list (only SECURITY.md:40, which is about the inbound host list)

**Geschlossen**
- The code layer is exemplary (frozenset, checked before every request and redirect hop, tested). But 3 of 5 applicable criteria (network layer, documentation, update procedure) are unmet → below half → fail by the rule. Remediation is mostly documentation; the network-layer control is realistically only achievable via a container/deployment (ties to SEC-007).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: SEC-004 (SSRF-Prevention) blockiert Requests an interne IP-Ranges. SEC-021 ergänzt das auf der **anderen Seite**: welche externen Ziele darf der Server überhaupt erreichen?

### Remediation

Add a README/SECURITY 'Egress' section: the only reachable host is api.discover.swiss (net.py EGRESS_ALLOWLIST), changes require a code PR + CHANGELOG entry; state that network-layer egress control is the deployer's responsibility and give a docker/NetworkPolicy example restricting egress to 443 on that host plus DNS.

**Disposition:** Egress is restricted in code (frozenset allow-list, checked on every request and redirect, tested). Network-layer control is the host's business for a local process; SECURITY.md will name the single allowed host and how to change it.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-021` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-024

## Finding: SEC-024 — Inbound Host/Origin-Allow-List (DNS-Rebinding auf den eigenen Endpoint)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-024` |
| **PDF-Reference** | Sec 4.4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- TransportSecuritySettings is never wired; protection exists only as the SDK's loopback auto-default (criterion 1 unmet)
- No deployment-configured allow-list (no MCP_ALLOWED_HOSTS or equivalent) — a non-loopback bind cannot be protected at all
- Entries are not port-exact (wrong port accepted) — the SDK default uses ':*'
- Non-loopback bind without allow-list is silent (no startup warning) — protection is fail-open exactly as the check describes
- No tests for wrong-port rejection / allowed-port acceptance or for auth-not-rescuing-foreign-host
- SECURITY.md documents a control that does not exist

### Expected Behavior

- [ ] **Evidence 1:** `TransportSecuritySettings` ist im Code an den Transport verdrahtet, mit `enable_dns_rebinding_protection=True`
- [ ] Die Allow-List stammt aus der Deployment-Konfiguration (`MCP_ALLOWED_HOSTS`), nicht aus dem Code
- [ ] Einträge sind portgenau — ein Eintrag trägt seinen Port
- [ ] Loopback ist immer enthalten, mit dem tatsächlich bedienten Port
- [ ] Konfigurierte CORS-Origins sind in der Origin-Liste des Transports enthalten
- [ ] `*` wird aus der CORS-Konfiguration **nicht** übernommen
- [ ] Fehlt die Variable auf einem Nicht-Loopback-Bind, bleibt der Schutz aus **und eine Startwarnung sagt es**
- [ ] **Evidence 2:** Ein Test weist «richtiger Hostname, falscher Port» ab — nicht nur einen fremden Namen —, und derselbe Name auf dem **richtigen** Port wird bedient. Erst das Paar schliesst eine zurückgefallene Default-Policy aus
- [ ] Ein Test belegt, dass ein gültiges Auth-Token einen fremden Host nicht rettet
- [ ] Die Allow-List erreicht **jeden** Netzpfad, über den der Server bedient werden kann

### Evidence

- src/discover_swiss_mcp/server.py:364-368 — mcp.streamable_http_app(host=settings.host) with no transport_security argument; grep 'TransportSecuritySettings|transport_security|allowed_hosts|allowed_origins|ALLOWED_HOSTS|enable_dns_rebinding_protection' in src/ → no hit (control: 16 hits in the SDK's mcpserver/server.py)
- .venv/.../mcp/server/mcpserver/server.py:1155-1159 (mcp 2.2.0) — SDK auto-enables protection only for host in 127.0.0.1/localhost/::1, with wildcard-port entries '127.0.0.1:*', 'localhost:*', '[::1]:*'
- runtime (audit, loopback bind): Host: evil.example.com → 421; foreign Origin → 403; allowed Host 127.0.0.1:<port> → 200; but Host: 127.0.0.1:9999 (wrong port) → 200 — list is not port-exact
- runtime (audit, DISCOVER_SWISS_MCP_HOST=0.0.0.0): Host: evil.example.com → 200 and foreign Origin → 200; start log has no warning
- SECURITY.md:39-41 — claims 'A non-loopback bind needs an explicit host allow-list', but the code offers no variable or mechanism to configure one

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:364-368 — mcp.streamable_http_app(host=settings.host) with no transport_security argument; grep 'TransportSecuritySettings|transport_security|allowed_hosts|allowed_origins|ALLOWED_HOSTS|enable_dns_rebinding_protection' in src/ → no hit (control: 16 hits in the SDK's mcpserver/server.py)
- .venv/.../mcp/server/mcpserver/server.py:1155-1159 (mcp 2.2.0) — SDK auto-enables protection only for host in 127.0.0.1/localhost/::1, with wildcard-port entries '127.0.0.1:*', 'localhost:*', '[::1]:*'
- runtime (audit, loopback bind): Host: evil.example.com → 421; foreign Origin → 403; allowed Host 127.0.0.1:<port> → 200; but Host: 127.0.0.1:9999 (wrong port) → 200 — list is not port-exact
- runtime (audit, DISCOVER_SWISS_MCP_HOST=0.0.0.0): Host: evil.example.com → 200 and foreign Origin → 200; start log has no warning
- SECURITY.md:39-41 — claims 'A non-loopback bind needs an explicit host allow-list', but the code offers no variable or mechanism to configure one

**Geschlossen**
- Only the loopback auto-protection of the SDK is present (foreign Host 421, foreign Origin 403 on 127.0.0.1). The explicit wiring, env-sourced port-exact list, warning and tests are all absent, and a 0.0.0.0 bind accepts any Host/Origin (runtime). Fewer than half the criteria met → fail.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Angriff ist DNS-Rebinding, aber die **eingehende** Variante: Eine Seite im Netz des Betreibers löst ihren eigenen Hostnamen auf die Adresse dieses MCP-Servers auf und spricht dann aus dem Browser mit ihm. Der Angreifer braucht keinen Netzzugang — er braucht nur, dass jemand im richtigen Netz seine Seite öffnet. Was er erbt, ist alles, was der Server kann: Tool-Inventar, Filesystem-Zugriffe, hinterlegte Credentials.

### Remediation

Add build_transport_security(host, port) reading DISCOVER_SWISS_MCP_ALLOWED_HOSTS / _ALLOWED_ORIGINS (port-exact, loopback entries with the served port always included, '*' dropped), pass transport_security= to streamable_http_app, log a WARNING when the bind is non-loopback and the variable is empty; add tests: allowed host:port → 200, same name wrong port → 421, foreign host → 421, and a mutation check (remove transport_security → wrong-port test fails). Align SECURITY.md with the implementation.

**Disposition:** Wire TransportSecuritySettings with a port-exact host and origin allow-list; SECURITY.md currently describes an allow-list the code does not have.

### Effort Estimate

S

### Dependencies / Blockers

Zusammen mit SEC-016 umsetzen (derselbe Startpfad).

### Verification After Fix

- Re-Audit von `SEC-024` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


### SEC-028

## Finding: SEC-028 — Egress-Guard: Policy-Verstoss und Auflösungsfehler sind unterscheidbar

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-028` |
| **PDF-Reference** | Custom (Katalog-Lücke, aufgefallen bei zh-education-mcp, 2026-08-03) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Policy violation and resolution failure are not distinguishable by a code-read discriminator; the empty-answer case shares EgressError with the policy case
- Transient resolver failures are never retried (gaierror bypasses the retry ladder; empty answer is re-raised as EgressError)
- User-facing message for an empty DNS answer names the egress policy — the exact misleading-message failure the check describes
- gaierror escapes status(): source_status, the diagnostic tool, fails instead of reporting reachable=false
- No tests for either the transient or the deterministic case with retry assertions

### Expected Behavior

- [ ] Policy-Verstoss und Auflösungsfehler verlassen den Guard als **verschiedene Exception-Typen** — oder als ein Typ mit einem Diskriminator, den der Code liest (Attribut, Enum), nicht als Text im Meldungsstring
- [ ] Die Retry-Politik entscheidet an diesem Diskriminator: Policy-Verstoss ohne Wiederholung, Auflösungsfehler mit
- [ ] Die nutzerseitige Meldung nennt im transienten Fall weder die Egress-Policy noch die Allow-List-Konfiguration als Ursache
- [ ] Kein Sammel-`except` und keine Fehlerabbildung, die die beiden Typen vor der Ausgabe wieder zusammenführt
- [ ] Beide Lagen sind getestet — der transiente Fall mit Wiederholung, der deterministische ohne; beide Tests fallen, wenn die Typen zusammengelegt werden

### Evidence

- src/discover_swiss_mcp/net.py:58-59 — a single EgressError(ValueError) type for all guard outcomes, no discriminator attribute
- src/discover_swiss_mcp/net.py:96-98 — an empty DNS answer raises EgressError('No DNS answer …') — the same type as a policy violation (net.py:100-103)
- src/discover_swiss_mcp/net.py:75-78 — loop.getaddrinfo is not wrapped: socket.gaierror escapes the guard untyped
- src/discover_swiss_mcp/client.py:729-730 — `except net.EgressError: raise` (never retried); client.py:731 retries only httpx.RequestError, which gaierror is not
- src/discover_swiss_mcp/server.py:218-219 — every EgressError is mapped to 'The outbound request was blocked by the server's egress policy.'
- src/discover_swiss_mcp/client.py:1103-1106 — status() catches DiscoverSwissError and EgressError only
- runtime (audit, socket.getaddrinfo raising gaierror EAI_AGAIN): client._call → socket.gaierror escapes, isEgressError False, isRequestError False, 1 attempt, 0 retries; client.status() raised gaierror (source_status would fail with 'unexpected internal error'); empty DNS answer → EgressError 'No DNS answer for …' which the tool layer reports as an egress-policy block

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:58-59 — a single EgressError(ValueError) type for all guard outcomes, no discriminator attribute
- src/discover_swiss_mcp/net.py:96-98 — an empty DNS answer raises EgressError('No DNS answer …') — the same type as a policy violation (net.py:100-103)
- src/discover_swiss_mcp/net.py:75-78 — loop.getaddrinfo is not wrapped: socket.gaierror escapes the guard untyped
- src/discover_swiss_mcp/client.py:729-730 — `except net.EgressError: raise` (never retried); client.py:731 retries only httpx.RequestError, which gaierror is not
- src/discover_swiss_mcp/server.py:218-219 — every EgressError is mapped to 'The outbound request was blocked by the server's egress policy.'
- src/discover_swiss_mcp/client.py:1103-1106 — status() catches DiscoverSwissError and EgressError only
- runtime (audit, socket.getaddrinfo raising gaierror EAI_AGAIN): client._call → socket.gaierror escapes, isEgressError False, isRequestError False, 1 attempt, 0 retries; client.status() raised gaierror (source_status would fail with 'unexpected internal error'); empty DNS answer → EgressError 'No DNS answer for …' which the tool layer reports as an egress-policy block

**Geschlossen**
- The guard throws one type for a policy violation and for an empty resolution, and lets a real resolver error escape untyped and unretried. Runtime probes confirm all three behaviours. 0 of 5 criteria met.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Egress-Guard scheitert an zwei grundverschiedenen Lagen, und beide laufen durch dieselbe Funktion:

### Remediation

In net.py add EgressPolicyViolation(EgressError, retryable=False) and EgressResolutionError(EgressError, retryable=True); wrap getaddrinfo (gaierror, OSError, empty answer) into EgressResolutionError; in client._call retry EgressResolutionError on the existing ladder and re-raise policy violations; in server._fail map the two to distinct messages (resolution: 'temporarily not resolvable, retry; configuration unaffected'); catch EgressResolutionError in status(); add the two tests from the check and run the merge-types mutation once.

**Disposition:** Split EgressError into a policy block and a resolution failure; retry only the latter, and stop status() from crashing on socket.gaierror.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-028` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)


---

## 6. Remediation-Plan

### Empfohlene Reihenfolge

1. **ARCH-005** (critical, partial)
2. **FID-001** (critical, partial)
3. **SEC-002** (critical, partial)
4. **SEC-004** (critical, partial)
5. **SEC-016** (critical, partial)
6. **ARCH-013** (high, partial)
7. **ARCH-014** (high, partial)
8. **ARCH-015** (high, partial)
9. **ARCH-016** (high, partial)
10. **DEP-001** (high, partial)
11. **DRIFT-002** (high, partial)
12. **DRIFT-004** (high, fail)
13. **DRIFT-008** (high, fail)
14. **FID-002** (high, partial)
15. **FID-003** (high, partial)
16. **FID-006** (high, fail)
17. **FID-007** (high, partial)
18. **IDENT-006** (high, partial)
19. **OBS-001** (high, partial)
20. **OPS-001** (high, fail)
21. **OPS-003** (high, fail)
22. **OPS-005** (high, partial)
23. **OPS-009** (high, partial)
24. **OPS-010** (high, fail)
25. **SEC-003** (high, fail)
26. **SEC-006** (high, partial)
27. **SEC-007** (high, fail)
28. **SEC-013** (high, partial)
29. **SEC-018** (high, partial)
30. **SEC-021** (high, fail)
31. **SEC-024** (high, fail)
32. **SEC-028** (high, fail)
33. **ARCH-002** (medium, partial)
34. **ARCH-003** (medium, fail)
35. **ARCH-008** (medium, fail)
36. **ARCH-011** (medium, partial)
37. **ARCH-012** (medium, fail)
38. **ARCH-018** (medium, partial)
39. **ARCH-020** (medium, fail)
40. **ARCH-021** (medium, partial)
41. **ARCH-022** (medium, partial)
42. **DRIFT-005** (medium, fail)
43. **DRIFT-006** (medium, partial)
44. **FID-004** (medium, partial)
45. **FID-005** (medium, fail)
46. **IDENT-002** (medium, partial)
47. **IDENT-003** (medium, partial)
48. **OBS-003** (medium, partial)
49. **OBS-007** (medium, partial)
50. **OBS-008** (medium, partial)
51. **OPS-002** (medium, partial)
52. **OPS-007** (medium, partial)
53. **OPS-008** (medium, fail)
54. **SCALE-010** (medium, partial)
55. **SDK-003** (medium, partial)
56. **IDENT-004** (low, partial)

---

## 7. Audit-Metadata

| Feld | Wert |
|---|---|
| skill_version | `2.3.0` |
| catalog_version | `2bbded9079fd` |
| applies_when_dsl_version | `1.0` |
| policy | `fail-or-partial` |
| audit_date | `2026-09-26` |


_Generated by tools/build_report.py — do not edit by hand._
