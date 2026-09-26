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
