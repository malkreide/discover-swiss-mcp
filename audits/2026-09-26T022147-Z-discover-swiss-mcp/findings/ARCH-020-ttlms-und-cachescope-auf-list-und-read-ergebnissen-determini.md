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
