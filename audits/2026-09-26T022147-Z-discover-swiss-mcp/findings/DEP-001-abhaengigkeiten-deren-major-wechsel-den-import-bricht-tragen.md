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
