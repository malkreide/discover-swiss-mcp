## Finding: SEC-021 — Egress-Allow-List: Code-Layer und Network-Layer

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-021` |
| **PDF-Reference** | Anhang B5 + B12 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No network-layer egress control (criterion 2) — none exists for the local process and none is documented as out of scope
- Allow-listed host is not documented in README or docs (criterion 3); only the net.py docstring states it
- No documented update procedure for allow-list changes (criterion 5)

### Expected Behavior

- [ ] Code-Layer Allow-List als `frozenset` im Code (nicht config-mutierbar)
- [ ] Network-Layer Egress Control via NetworkPolicy / Security Group / Cloudflare WARP
- [ ] Allow-List-Hosts dokumentiert in `docs/network-egress.md` oder README
- [ ] Pre-Request-Check (`assert_host_allowed`) wird vor jedem ausgehenden Request aufgerufen
- [ ] Update-Verfahren für Allow-List-Erweiterungen dokumentiert
- [ ] DNS-Resolution-Path im Network-Layer explizit erlaubt (sonst Hostname-Lookup bricht)

### Evidence

- src/discover_swiss_mcp/net.py:34 — EGRESS_ALLOWLIST: frozenset[str] = frozenset({'api.discover.swiss'}) (immutable, not env-derived)
- src/discover_swiss_mcp/net.py:67-72,95 — assert_host_allowed called inside assert_url_allowed; net.py:133-134 — runs before every outbound request and on every redirect hop; client.py:717 — the only outbound call site uses net.safe_request
- tests/test_net.py:12-14 (non-allow-listed host rejected), tests/test_net.py:75-87 (redirect to evil.example stopped)
- src/discover_swiss_mcp/config.py:127 — DISCOVER_SWISS_BASE_URL is configurable, but a different host still fails the frozenset check (net.py:95)
- repo — no NetworkPolicy/SecurityGroup/compose/egress config (find + git ls-files, control fires on pyproject.toml); grep 'allow-list|allowlist|api\.discover\.swiss|egress' in README.md/README.de.md/docs/*.md/CHANGELOG.md → no documentation of the egress allow-list (only SECURITY.md:40, which is about the inbound host list)

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:34 — EGRESS_ALLOWLIST: frozenset[str] = frozenset({'api.discover.swiss'}) (immutable, not env-derived)
- src/discover_swiss_mcp/net.py:67-72,95 — assert_host_allowed called inside assert_url_allowed; net.py:133-134 — runs before every outbound request and on every redirect hop; client.py:717 — the only outbound call site uses net.safe_request
- tests/test_net.py:12-14 (non-allow-listed host rejected), tests/test_net.py:75-87 (redirect to evil.example stopped)
- src/discover_swiss_mcp/config.py:127 — DISCOVER_SWISS_BASE_URL is configurable, but a different host still fails the frozenset check (net.py:95)
- repo — no NetworkPolicy/SecurityGroup/compose/egress config (find + git ls-files, control fires on pyproject.toml); grep 'allow-list|allowlist|api\.discover\.swiss|egress' in README.md/README.de.md/docs/*.md/CHANGELOG.md → no documentation of the egress allow-list (only SECURITY.md:40, which is about the inbound host list)

**Geschlossen**
- The code layer is exemplary (frozenset, checked before every request and redirect hop, tested). But 3 of 5 applicable criteria (network layer, documentation, update procedure) are unmet → below half → fail by the rule. Remediation is mostly documentation; the network-layer control is realistically only achievable via a container/deployment (ties to SEC-007).

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: SEC-004 (SSRF-Prevention) blockiert Requests an interne IP-Ranges. SEC-021 ergänzt das auf der **anderen Seite**: welche externen Ziele darf der Server überhaupt erreichen?

### Remediation

Add a README/SECURITY 'Egress' section: the only reachable host is api.discover.swiss (net.py EGRESS_ALLOWLIST), changes require a code PR + CHANGELOG entry; state that network-layer egress control is the deployer's responsibility and give a docker/NetworkPolicy example restricting egress to 443 on that host plus DNS.

**Disposition:** Egress is restricted in code (frozenset allow-list, checked on every request and redirect, tested). Network-layer control is the host's business for a local process; SECURITY.md will name the single allowed host and how to change it.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-021` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
