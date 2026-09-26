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
