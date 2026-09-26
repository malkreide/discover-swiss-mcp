## Finding: ARCH-005 — Keine Hardcoded Secrets: Env-Vars / Secret Manager only

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-005` |
| **PDF-Reference** | Sec 2.1 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- .env.example with placeholders does not exist (and .gitignore:16 '.env.*' would also ignore it — no '!.env.example' exception)
- No gitleaks/trufflehog (or equivalent) secret-scan step in .github/workflows/ci.yml or publish.yml
- Settings are hand-rolled from os.environ rather than pydantic-settings (accepted as 'o.ä.', noted only)

### Expected Behavior

- [ ] Keine API-Keys, Passwörter, Tokens, Connection-Strings im Source-Code
- [ ] Keine Default-Werte mit echten Secrets in `os.environ.get(..., default=...)` oder ähnlich
- [ ] Secrets werden zur Startzeit aus Env-Vars / Secret-Manager geladen (Pydantic-Settings o.ä.)
- [ ] In-Memory-Repräsentation als `SecretStr` (Python) oder gleichwertig (kein `str`)
- [ ] Secrets erscheinen **nicht** in Log-Outputs (keine `f"{settings}"`-Logs)
- [ ] `.gitignore` enthält `.env`, `.env.*` (ausser `.env.example`)
- [ ] `.env.example` mit Platzhaltern existiert und ist im Repo
- [ ] CI-Workflow mit Gitleaks oder Trufflehog läuft auf PRs

### Evidence

- src/discover_swiss_mcp/config.py:45,91,125 — api_key is SecretStr read from DISCOVER_SWISS_KEY with empty default (no real key as fallback)
- src/discover_swiss_mcp/config.py:58-76 and server.py:129-134 — only safe_summary() is logged ('api_key': 'set'|'missing'); runtime startup log line shows "api_key": "set"
- .gitignore:15-16 — .env and .env.* ignored
- grep secret pattern (api_key|password|secret|token = '16+ chars') over src/ → 0 hits (negative control: fires on a scratch file with api_key = "abcdefghijklmnopqrstuvwx"); AKIA/connection-string patterns → 0 hits; git grep over tracked files shows the key only as env reads in probes/*.py (e.g. probes/probe_detail.py:28)
- attempted gitleaks/trufflehog: neither installed in this environment (which → not found); history grep for 32-hex subscription-key values → no hits

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:45,91,125 — api_key is SecretStr read from DISCOVER_SWISS_KEY with empty default (no real key as fallback)
- src/discover_swiss_mcp/config.py:58-76 and server.py:129-134 — only safe_summary() is logged ('api_key': 'set'|'missing'); runtime startup log line shows "api_key": "set"
- .gitignore:15-16 — .env and .env.* ignored
- grep secret pattern (api_key|password|secret|token = '16+ chars') over src/ → 0 hits (negative control: fires on a scratch file with api_key = "abcdefghijklmnopqrstuvwx"); AKIA/connection-string patterns → 0 hits; git grep over tracked files shows the key only as env reads in probes/*.py (e.g. probes/probe_detail.py:28)
- attempted gitleaks/trufflehog: neither installed in this environment (which → not found); history grep for 32-hex subscription-key values → no hits

**Geschlossen**
- No secret in code or history found; key handling (SecretStr, masked summary, env only) is exemplary. Two of eight criteria (.env.example, CI secret scan) are unmet, so not a pass on a critical check; no leak evidence, gitleaks not runnable here.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Hardcoded Secrets (API-Keys, Passwörter, Tokens, Connection-Strings, Encryption-Keys) im Source-Code sind die häufigste vermeidbare Sicherheitsschwäche in MCP-Server-Repositories. Sobald das Repo öffentlich ist (oder versehentlich öffentlich wird), oder ein Mitarbeiter aus dem Team ausscheidet, sind alle Secrets kompromittiert.

### Remediation

Add .env.example with DISCOVER_SWISS_KEY=replace-with-your-key and '!.env.example' in .gitignore; add a gitleaks-action job (SHA-pinned) on push/pull_request.

**Disposition:** Add .env.example with placeholders and a '!.env.example' exception in .gitignore; add a secret scan step to CI.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-005` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
