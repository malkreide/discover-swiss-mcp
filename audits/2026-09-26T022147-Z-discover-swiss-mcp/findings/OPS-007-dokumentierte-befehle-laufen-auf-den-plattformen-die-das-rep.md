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
