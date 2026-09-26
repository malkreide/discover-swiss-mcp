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
