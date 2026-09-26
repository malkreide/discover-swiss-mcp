## Finding: IDENT-002 — __version__ aus der installierten Distribution, nicht von Hand gepflegt

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `IDENT-002` |
| **PDF-Reference** | Custom (Portfolio-Sweep 2026-07-29, 30 Server) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No version invariant test: tests/test_smoke.py:18-20 only asserts __version__ is a non-empty string; nothing compares __version__ with server.json or pyproject.toml
- Consequently no detuned-server.json counter-test, no editable-install hint in a failure message, no skip-without-install behaviour
- Observation outside the criteria: src/discover_swiss_mcp/server.py:147-161 builds MCPServer without version=__version__; serverInfo.version on the wire is '' (stdio initialize from the wheel-installed entry point returned {'name': 'discover_swiss_mcp', 'version': ''})

### Expected Behavior

- [ ] `__version__` wird über `importlib.metadata.version()` (bzw. das Sprach-Äquivalent) gelesen
- [ ] Kein Versionsliteral unter `src/` ausser dem Fallback-Marker (IDENT-005)
- [ ] **Kein Versionsliteral unter `tests/`** — ein Test, der die Nummer festnagelt, ist selbst eine Versions-Stelle
- [ ] Der Versions-Test vergleicht eine **Invariante** zwischen zwei unabhängig gepflegten Stellen (`__version__` gegen `server.json`), nicht `__version__` gegen eine aufgeschriebene Zahl
- [ ] Dieser Test wurde durch **Verstimmen von `server.json`** einmal rot gesehen — sonst ist unbelegt, dass er greift
- [ ] Ein Test vergleicht die installierten Metadaten gegen `pyproject.toml`
- [ ] Die Fehlermeldung dieses Tests nennt den Editable-Install-Fall
- [ ] Der Test wird ohne Installation **übersprungen**, nicht rot (sonst scheitert er im reinen Quell-Checkout)
- [ ] Bei Submodul-Importen in `__init__.py`: Versionsblock steht **vor** ihnen (Zirkelimport)
- [ ] Aus dem Bestehen dieses Checks wurde **nicht** auf die Identität des publizierten Pakets geschlossen — dafür sind `IDENT-001` (Modus 3) und `IDENT-006` zuständig

### Evidence

- src/discover_swiss_mcp/__init__.py:9-18 — __version__ = importlib.metadata.version('discover-swiss-mcp'), PackageNotFoundError fallback '0.0.0+source'
- grep -rnE '__version__\s*=\s*"[0-9]+\.[0-9]' src/ | grep -v '+' -> no hit; control '__version__ = "0.1.0"' matches
- grep -rnE '__version__\s*==\s*"[0-9]+\.[0-9]|==\s*"v?[0-9]+\.[0-9]+\.[0-9]+"' tests/ -> no hit; control 'assert __version__ == "0.3.0"' matches
- src/discover_swiss_mcp/__init__.py — imports no submodule, so no circular-import ordering risk
- Runtime: import discover_swiss_mcp -> __version__ 0.1.0 == pyproject.toml:7

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/__init__.py:9-18 — __version__ = importlib.metadata.version('discover-swiss-mcp'), PackageNotFoundError fallback '0.0.0+source'
- grep -rnE '__version__\s*=\s*"[0-9]+\.[0-9]' src/ | grep -v '+' -> no hit; control '__version__ = "0.1.0"' matches
- grep -rnE '__version__\s*==\s*"[0-9]+\.[0-9]|==\s*"v?[0-9]+\.[0-9]+\.[0-9]+"' tests/ -> no hit; control 'assert __version__ == "0.3.0"' matches
- src/discover_swiss_mcp/__init__.py — imports no submodule, so no circular-import ordering risk
- Runtime: import discover_swiss_mcp -> __version__ 0.1.0 == pyproject.toml:7

**Geschlossen**
- 5 of 10 criteria met: derivation is correct and literal-free, but no test holds the invariant, so the check's own counter-test cannot exist.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Der Portfolio-Sweep vom 2026-07-29 fand **20 von 30 Servern** mit abgedriftetem `__version__`:

### Remediation

Add tests/test_version.py: assert __version__ == json.loads(server.json)['version'] and == tomllib pyproject version (skip on '+source'), message mentions re-running pip install -e .; detune server.json once to see it fail. Pass version=__version__ to MCPServer.

**Disposition:** Add a test that __version__ equals pyproject.toml and server.json.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `IDENT-002` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
