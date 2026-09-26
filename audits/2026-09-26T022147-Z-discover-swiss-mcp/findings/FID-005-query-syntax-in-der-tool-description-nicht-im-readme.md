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
