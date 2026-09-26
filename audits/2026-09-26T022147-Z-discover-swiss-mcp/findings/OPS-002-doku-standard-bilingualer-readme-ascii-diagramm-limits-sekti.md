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
