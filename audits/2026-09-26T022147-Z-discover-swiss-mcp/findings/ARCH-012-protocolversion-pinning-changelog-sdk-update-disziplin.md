## Finding: ARCH-012 — protocolVersion-Pinning + CHANGELOG + SDK-Update-Disziplin

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-012` |
| **PDF-Reference** | Anhang A9 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Pinned constant is decorative: the per-request check and -32022 come from the SDK's own list, not from MCP_PROTOCOL_VERSION; legacy handshake versions (2024-11-05..2025-11-25) are still accepted
- Code comment asserts a guard test that does not exist
- CHANGELOG does not name the spec version
- README has no 'MCP Protocol Version' section and no update/breaking-change policy
- No Dependabot/Renovate for pip (SDK updates are not proposed)

### Expected Behavior

- [ ] `protocolVersion` ist im Server-Code explizit gepinnt (kein «latest», kein Default)
- [ ] Auf `2026-07-28`: Die gepinnte Version wird **pro Request** gegen `io.modelcontextprotocol/protocolVersion` aus `_meta` geprüft — eine Konstante ohne diesen Vergleich zählt nicht
- [ ] Auf `2026-07-28`: Nichtübereinstimmung liefert `UnsupportedProtocolVersionError` (`-32022`), und `server/discover` nennt dieselbe Versionsliste (`ARCH-016`)
- [ ] `CHANGELOG.md` vorhanden, im Keep-a-Changelog-Format
- [ ] CHANGELOG-Einträge nennen explizit Spec-Version-Bumps
- [ ] README hat Sektion «MCP Protocol Version» mit aktuell unterstützter Version
- [ ] Update-Policy im README dokumentiert
- [ ] Dependabot oder Renovate aktiv für monatliche SDK-Update-PRs

### Evidence

- src/discover_swiss_mcp/server.py:73 — MCP_PROTOCOL_VERSION = "2026-07-28"; used only in the startup log (:131) and tests/test_server.py:152 (snapshot equality), never passed to MCPServer or compared with _meta
- src/discover_swiss_mcp/server.py:69-72 — comment claims 'a test holds the constant against the SDK's own LATEST_PROTOCOL_VERSION'; grep LATEST_PROTOCOL_VERSION tests/ scripts/ → 0 hits (negative control: hits .venv/.../mcp_types/version.py:50) — the test does not exist
- runtime (streamable-http): tools/list with _meta protocolVersion 2030-01-01 → error -32022 data.supported ['2026-07-28'] (SDK mcp_types/version.py:41 MODERN_PROTOCOL_VERSIONS); server/discover supportedVersions ['2026-07-28']
- runtime: legacy initialize with protocolVersion 2025-06-18 → 200, negotiated 2025-06-18 — the pinned constant does not constrain what the server speaks
- CHANGELOG.md:1-8 — Keep a Changelog header; CHANGELOG.md:63-64 says 'pinned protocol version' without naming it
- grep -iE 'breaking|spec.version|protocol.version|migration' README.md README.de.md → 0 hits (negative control: 27 hits in ARCH-012.md)
- .github/dependabot.yml — only package-ecosystem github-actions, no pip

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/server.py:73 — MCP_PROTOCOL_VERSION = "2026-07-28"; used only in the startup log (:131) and tests/test_server.py:152 (snapshot equality), never passed to MCPServer or compared with _meta
- src/discover_swiss_mcp/server.py:69-72 — comment claims 'a test holds the constant against the SDK's own LATEST_PROTOCOL_VERSION'; grep LATEST_PROTOCOL_VERSION tests/ scripts/ → 0 hits (negative control: hits .venv/.../mcp_types/version.py:50) — the test does not exist
- runtime (streamable-http): tools/list with _meta protocolVersion 2030-01-01 → error -32022 data.supported ['2026-07-28'] (SDK mcp_types/version.py:41 MODERN_PROTOCOL_VERSIONS); server/discover supportedVersions ['2026-07-28']
- runtime: legacy initialize with protocolVersion 2025-06-18 → 200, negotiated 2025-06-18 — the pinned constant does not constrain what the server speaks
- CHANGELOG.md:1-8 — Keep a Changelog header; CHANGELOG.md:63-64 says 'pinned protocol version' without naming it
- grep -iE 'breaking|spec.version|protocol.version|migration' README.md README.de.md → 0 hits (negative control: 27 hits in ARCH-012.md)
- .github/dependabot.yml — only package-ecosystem github-actions, no pip

**Geschlossen**
- Met: CHANGELOG format; -32022 and discover list consistent (via SDK). Not met: an enforced server-side pin, CHANGELOG spec references, README section, update policy, SDK update automation. Fewer than half.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die MCP-Spec hat in 21 Monaten fünf Major-Updates erlebt (2024-11, 2025-03, 2025-06, 2025-11, 2026-07). Das ist eine ungewöhnlich hohe Velocity für einen Industriestandard. Konkrete Folgen für Server-Maintainer:

### Remediation

Add the promised test (MCP_PROTOCOL_VERSION in mcp_types.MODERN_PROTOCOL_VERSIONS and == server/discover supportedVersions); decide whether legacy handshake eras should be served (stateless_http / legacy off) and document it; add README/README.de 'MCP Protocol Version' section with update policy; name '2026-07-28' in CHANGELOG; add a pip ecosystem to .github/dependabot.yml grouping mcp.

**Disposition:** The pinned protocol version is not enforced and the comment in server.py promises a test that does not exist. Add the test against the SDK's LATEST_PROTOCOL_VERSION and correct the comment.

### Effort Estimate

S

### Dependencies / Blockers

Zusammen mit ARCH-015 und ARCH-016 (Protokoll-Identität).

### Verification After Fix

- Re-Audit von `ARCH-012` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
