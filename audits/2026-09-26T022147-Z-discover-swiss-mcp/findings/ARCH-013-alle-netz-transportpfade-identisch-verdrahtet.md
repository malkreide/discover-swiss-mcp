## Finding: ARCH-013 — Alle Netz-Transportpfade identisch verdrahtet

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-013` |
| **PDF-Reference** | Sec 2.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No test exercises the seam main() → streamable_http_app(host=…) (grep tests/ for streamable_http_app/transport/main → none); no mutation Gegenprobe
- Host-allow-list protection is armed only when DISCOVER_SWISS_MCP_HOST is loopback; a non-loopback bind silently runs without transport_security (documented only as 'localhost only' default, README.md:142)

### Expected Behavior

- [ ] Alle Codepfade, die eine ASGI-App konstruieren oder servieren, sind aufgezählt — eigener Builder, `run()`-Pfad, SSE, Factory
- [ ] Die Deployment-Manifeste sind mitgelesen; ein dort verdrahteter Pfad (`--factory`, eigener `CMD`) zählt mit
- [ ] Die Sicherheitsverdrahtung ist auf **allen** identisch, nicht nur auf dem bedingten Zweig
- [ ] Kein Scharfschalten hängt an einer sachfremden Bedingung (Auth gesetzt, CORS gesetzt, Debug aus)
- [ ] Der **vollständige** Bind-Parametersatz reist mit — Host **und** Port, nicht nur der Host
- [ ] Eine `uvicorn --factory` liest den Bind selbst aus derselben Quelle wie `main()`
- [ ] Pro Pfad existiert ein Test, der die Verdrahtung an der Naht prüft, nicht nur im Builder
- [ ] Gegenprobe geführt: Verdrahtung aus je einem Pfad entfernt, jedes Mal scheitert mindestens ein Test

### Evidence

- Path enumeration (grep streamable_http_app|sse_app|http_app|mcp.run|uvicorn.run in src/): server.py:364-368 uvicorn.run(mcp.streamable_http_app(host=settings.host), host=settings.host, port=settings.port) and server.py:370 mcp.run() (stdio) — no SSE app, no factory
- Deployment manifests: no Dockerfile/railway.toml/render.yaml/Procfile/docker-compose; pyproject.toml:58-59 console script → discover_swiss_mcp.server:main (same main as __main__.py:8-10)
- .venv/.../mcp/server/lowlevel/server.py:741-747 — SDK enables DNS-rebinding protection with allowed_hosts 127.0.0.1:*, localhost:*, [::1]:* (port wildcard, so the port need not travel) when host is loopback
- runtime: POST /mcp with Host: evil.example.com → 421, with Host: 127.0.0.1:8768 → 200; GET /mcp → 400 (no server-initiated GET stream)

### Gemessen / Geschlossen / Offen

**Gemessen**
- Path enumeration (grep streamable_http_app|sse_app|http_app|mcp.run|uvicorn.run in src/): server.py:364-368 uvicorn.run(mcp.streamable_http_app(host=settings.host), host=settings.host, port=settings.port) and server.py:370 mcp.run() (stdio) — no SSE app, no factory
- Deployment manifests: no Dockerfile/railway.toml/render.yaml/Procfile/docker-compose; pyproject.toml:58-59 console script → discover_swiss_mcp.server:main (same main as __main__.py:8-10)
- .venv/.../mcp/server/lowlevel/server.py:741-747 — SDK enables DNS-rebinding protection with allowed_hosts 127.0.0.1:*, localhost:*, [::1]:* (port wildcard, so the port need not travel) when host is loopback
- runtime: POST /mcp with Host: evil.example.com → 421, with Host: 127.0.0.1:8768 → 200; GET /mcp → 400 (no server-initiated GET stream)

**Geschlossen**
- Only one network path exists and it carries the SDK host allow-list, verified at runtime. The per-path seam test and the counter-proof are missing, which blocks pass on a high check.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Ein Server, der über Netz erreichbar ist, konstruiert seine ASGI-App fast nie an genau einer Stelle. Typisch sind drei bis vier Wege, und sie entstehen nacheinander, ohne dass jemand sie als Menge betrachtet:

### Remediation

Add a test that calls main() with DISCOVER_SWISS_MCP_TRANSPORT=streamable-http (uvicorn.run monkeypatched) and asserts the app rejects Host: evil.example.com with 421; run it once with host= removed to see it fail; pass explicit transport_security for non-loopback hosts or refuse them.

**Disposition:** Add a test for the main() to streamable_http_app(host=...) seam.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-013` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
