## Finding: SEC-004 — SSRF-Prevention: HTTPS-Enforcement + IP-Blocklisting

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-004` |
| **PDF-Reference** | Sec 4.4 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- IPv4-mapped IPv6 answers bypass the blocklist: ::ffff:169.254.169.254 and ::ffff:127.0.0.1 are not blocked (ipaddress compares across versions as not-contained). Exploitation requires control of DNS for api.discover.swiss because the host allow-list (net.py:34, 95) restricts targets first — compensated, not closed
- Unspecified (::), multicast (224.0.0.0/4), benchmark (198.18.0.0/15), reserved (240.0.0.0/4) and NAT64 (64:ff9b::/96) ranges not blocked
- No egress proxy (criterion 5) — not applicable in practice: server is local-only, not production/cloud deployed

### Expected Behavior

- [ ] HTTPS-Schema wird vor jedem ausgehenden Request validiert
- [ ] Resolved IP wird gegen Blocklist (private + link-local + loopback) geprüft
- [ ] Cloud-Metadata-IP `169.254.169.254` ist explizit blockiert
- [ ] IPv6-Loopback (`::1`) und IPv6-Link-local (`fe80::/10`) sind blockiert
- [ ] In Production: Egress-Proxy (Smokescreen o.ä.) als Defense-in-Depth

**Nicht hier bewertet: DNS-Pinning.** Ob die geprüfte IP auch die benutzte IP ist, prüft `SEC-005`. Das Pass-Pattern oben löst bereits einmal auf und verwendet die IP — echter Code macht beides in derselben Funktion —, aber das **Kriterium** gehört dorthin, nicht hierher.

Der Grund ist `SKILL.md` §2.5: Zwei Checks, die einander überlappen, doppeln das Finding, und wenn der Server die Ursache behebt, bleibt der zweite rot — der Fix sieht aus, als hätte er nicht gewirkt. Bis v1.3.1 stand «DNS-Resolution erfolgt einmal» wortgleich in beiden Checks.

Zusammengelegt wurden sie trotzdem nicht: Blocklisting und Pinning sind **getrennt behebbar**, und §2.5 verlangt, dass ein Check in *einem* Schritt behebbar bleibt. Ein Server kann die Blockliste korrekt führen und trotzdem zweimal auflösen — das sind zwei Befunde mit zwei Remediationen, nicht einer.

### Evidence

- src/discover_swiss_mcp/net.py:93-94 — scheme != 'https' raises EgressError before any request (test: tests/test_net.py:17-19)
- src/discover_swiss_mcp/net.py:96-103 — host resolved once, every resolved IP checked against BLOCKED_NETWORKS before the request
- src/discover_swiss_mcp/net.py:39-53 — blocklist: 0.0.0.0/8, 10/8, 100.64/10, 127/8, 169.254/16 (covers 169.254.169.254), 172.16/12, 192.168/16, ::1/128, fc00::/7, fe80::/10
- src/discover_swiss_mcp/net.py:133-134 — safe_request re-runs the full check on every redirect hop; tests/test_net.py:75-87 (redirect off allow-list stopped)
- tests/test_net.py:22-35 — parametrized block test for 127.0.0.1, 10.0.0.5, 192.168.1.1, 169.254.169.254, ::1 (215 offline tests pass)
- runtime (audit): net._is_blocked_ip → 169.254.169.254 True, ::1 True, fe80::1 True, fd00::1 True (controls), but ::ffff:169.254.169.254 False, ::ffff:127.0.0.1 False, '::' False, 224.0.0.1 False, 198.18.0.1 False, 64:ff9b::a9fe:a9fe False

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/net.py:93-94 — scheme != 'https' raises EgressError before any request (test: tests/test_net.py:17-19)
- src/discover_swiss_mcp/net.py:96-103 — host resolved once, every resolved IP checked against BLOCKED_NETWORKS before the request
- src/discover_swiss_mcp/net.py:39-53 — blocklist: 0.0.0.0/8, 10/8, 100.64/10, 127/8, 169.254/16 (covers 169.254.169.254), 172.16/12, 192.168/16, ::1/128, fc00::/7, fe80::/10
- src/discover_swiss_mcp/net.py:133-134 — safe_request re-runs the full check on every redirect hop; tests/test_net.py:75-87 (redirect off allow-list stopped)
- tests/test_net.py:22-35 — parametrized block test for 127.0.0.1, 10.0.0.5, 192.168.1.1, 169.254.169.254, ::1 (215 offline tests pass)
- runtime (audit): net._is_blocked_ip → 169.254.169.254 True, ::1 True, fe80::1 True, fd00::1 True (controls), but ::ffff:169.254.169.254 False, ::ffff:127.0.0.1 False, '::' False, 224.0.0.1 False, 198.18.0.1 False, 64:ff9b::a9fe:a9fe False

**Geschlossen**
- HTTPS enforcement, post-resolution IP check, metadata and IPv6 loopback/link-local blocking are all present with tests. The blocklist is range-based on the raw address and misses IPv4-mapped IPv6 forms of the blocked ranges — the 'IPv6-mapped' trick named in the check. Because the host allow-list admits only api.discover.swiss, the gap is not reachable via tool arguments, so it is rated below critical; still a gap in criterion 2/3 → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Server-Side Request Forgery (SSRF) entsteht, wenn ein MCP-Server URLs aus User-Input (oder LLM-generierten Args) direkt an HTTP-Clients weitergibt. Ein Angreifer kann den Server dann zwingen, beliebige interne Adressen abzurufen — insbesondere die Cloud-Metadata-Endpunkte.

### Remediation

In _is_blocked_ip: unwrap ip.ipv4_mapped (and ip.sixtofour / NAT64 if desired) before the range check, and additionally reject ip.is_private, is_loopback, is_link_local, is_multicast, is_reserved, is_unspecified; add ::ffff:169.254.169.254 and ::ffff:127.0.0.1 to the parametrized test in tests/test_net.py.

**Disposition:** IPv4-mapped IPv6 addresses bypass the blocklist (::ffff:169.254.169.254, ::ffff:127.0.0.1 verified). Unwrap ipv4_mapped before the check; add tests.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-004` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
