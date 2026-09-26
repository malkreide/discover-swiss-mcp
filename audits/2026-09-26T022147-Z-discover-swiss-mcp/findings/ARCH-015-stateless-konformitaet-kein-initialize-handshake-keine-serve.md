## Finding: ARCH-015 — Stateless-Konformität: kein initialize-Handshake, keine Server-Sitzung

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-015` |
| **PDF-Reference** | SEP-2575, SEP-2567 |
| **Adoption** | advisory |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- SDK serves the legacy era: POST initialize with protocolVersion 2025-06-18 over HTTP returns 200 and sets an mcp-session-id header — the server still issues session ids although it pins 2026-07-28 (streamable_http_app called without stateless_http, server.py:365)
- No order-independence test and no Gegenprobe against a stateful variant

### Expected Behavior

- [ ] Kein `initialize`- / `initialized`-Handler im eigenen Code
- [ ] Kein `Mcp-Session-Id` gelesen, gesetzt oder geroutet
- [ ] Protokollversion und Client-Capabilities werden **pro Request** aus `_meta` gelesen, nicht aus gespeichertem Verhandlungsergebnis
- [ ] Bei nicht unterstützter Version antwortet der Server mit `UnsupportedProtocolVersionError` (`-32022`), nicht mit einem generischen Fehler
- [ ] Keine prozesslokale Struktur trägt Aufrufer-bezogenen Zustand über Requests hinweg — geprüft am Code, nicht nur am Namen
- [ ] Die List-Antworten variieren nicht pro Verbindung
- [ ] **Gegenprobe:** Der Reihenfolge-Test ist einmal gegen eine absichtlich zustandsbehaftete Fassung gelaufen und hat dort angeschlagen. Ein Test, der nur die grüne Richtung kennt, belegt nichts

### Evidence

- grep 'initialize|notifications/initialized|InitializeResult|InitializationOptions' src/ → 0; grep 'mcp-session-id|session_manager|SessionManager|sessionId' src/ → 0 (negative controls: 10 and 9 hits in .venv/.../mcp/server/lowlevel/server.py)
- runtime: request with _meta protocolVersion 2030-01-01 → -32022 'Unsupported protocol version' (per-request version check by SDK)
- module-level container grep '^_?[A-Z_]+ … = {}|[]' src/ → 0 (control fires on scratch file); broader scan shows only constants (client.py:190, tools.py:101…); instance state client.py:612-614 is source state (quota, last success, search availability), client.py:387-445 rate bucket and TTL cache are source-derived
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random; tools registered at import (server.py:230-335)

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep 'initialize|notifications/initialized|InitializeResult|InitializationOptions' src/ → 0; grep 'mcp-session-id|session_manager|SessionManager|sessionId' src/ → 0 (negative controls: 10 and 9 hits in .venv/.../mcp/server/lowlevel/server.py)
- runtime: request with _meta protocolVersion 2030-01-01 → -32022 'Unsupported protocol version' (per-request version check by SDK)
- module-level container grep '^_?[A-Z_]+ … = {}|[]' src/ → 0 (control fires on scratch file); broader scan shows only constants (client.py:190, tools.py:101…); instance state client.py:612-614 is source state (quota, last success, search availability), client.py:387-445 rate bucket and TTL cache are source-derived
- runtime: tools/list order identical across 3 fresh processes with PYTHONHASHSEED=random; tools registered at import (server.py:230-335)

**Geschlossen**
- Own code is stateless and version/caps are read per request by the SDK; the remaining gaps are the SDK's dual-era session issuance on HTTP and the missing test with counter-proof.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Mit `2026-07-28` fällt der Lebenszyklus weg, um den herum jeder MCP-Server bisher gebaut wurde. Zwei Entscheidungen, die zusammengehören:

### Remediation

Pass stateless_http=True (or otherwise disable the legacy handshake) in mcp.streamable_http_app and document it; add a test that interleaves two tool calls in different order across two Client sessions and assert identical results, and run it once against a deliberately stateful variant.

**Disposition:** The SDK (mcp 2.2.0) still answers a legacy initialize over HTTP and issues mcp-session-id; the server keeps no state of its own. Accepted until the SDK offers a switch; re-check at the next SDK minor.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-015` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
