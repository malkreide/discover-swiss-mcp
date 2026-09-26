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
