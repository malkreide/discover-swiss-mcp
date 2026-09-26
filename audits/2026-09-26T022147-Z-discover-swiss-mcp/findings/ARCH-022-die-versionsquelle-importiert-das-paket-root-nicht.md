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
