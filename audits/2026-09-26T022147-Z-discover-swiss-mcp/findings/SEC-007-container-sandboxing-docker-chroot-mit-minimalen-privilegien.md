## Finding: SEC-007 — Container-Sandboxing: Docker / chroot mit minimalen Privilegien

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | fail |
| **Status** | accepted-risk |
| **Disposition** | akzeptiert (accepted-risk) |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-007` |
| **PDF-Reference** | Sec 4.5 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- No container image or sandbox of any kind: no non-root USER, no read-only root FS, no dropped capabilities, no seccomp profile (criteria 1-5 unmet)
- Server runs as the local user with access to that user's files and environment (including DISCOVER_SWISS_KEY and any other secrets in the MCP host's env)

### Expected Behavior

- [ ] Dockerfile setzt `USER` mit nicht-root UID (≥ 10000)
- [ ] Bei Kubernetes: `runAsNonRoot: true`, `runAsUser` explizit, `allowPrivilegeEscalation: false`
- [ ] Bei Kubernetes: `readOnlyRootFilesystem: true` mit `tmpfs`-Volume für `/tmp`
- [ ] Bei Kubernetes: `capabilities.drop: ["ALL"]`
- [ ] seccomp-Profile mindestens `RuntimeDefault`
- [ ] Bei File-Tools: Volume-Mounts nur für erlaubte Pfade, ggf. read-only

### Evidence

- repo — `find` for Dockerfile*, *compose*.y*ml, railway.toml, render.yaml, k8s/, helm/ (excluding .venv) returns nothing; control: same find expression matches ./pyproject.toml; `git ls-files | grep -iE 'docker|compose|k8s|helm|railway|render'` → no match (91 tracked files)
- README.md:127-143 — only documented run mode is pip install -e + `python -m discover_swiss_mcp` directly on the host, with user privileges
- src/ — no file-system tools (grep 'open\(|Path\(' in src/ → no file access), so criterion 6 is not applicable

### Gemessen / Geschlossen / Offen

**Gemessen**
- repo — `find` for Dockerfile*, *compose*.y*ml, railway.toml, render.yaml, k8s/, helm/ (excluding .venv) returns nothing; control: same find expression matches ./pyproject.toml; `git ls-files | grep -iE 'docker|compose|k8s|helm|railway|render'` → no match (91 tracked files)
- README.md:127-143 — only documented run mode is pip install -e + `python -m discover_swiss_mcp` directly on the host, with user privileges
- src/ — no file-system tools (grep 'open\(|Path\(' in src/ → no file access), so criterion 6 is not applicable

**Geschlossen**
- The check applies to local-stdio deployments. The server ships no sandboxing mechanism and documents none; all applicable criteria are unmet. Risk is moderated by a small dependency set and read-only, no-filesystem tool code, but that is not a sandbox.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Lokale stdio-Server (siehe SEC-006) eliminieren die Netzwerk-Angriffsfläche, behalten aber das Risiko, dass ein kompromittierter Server-Code (durch Supply-Chain-Attack, böswilliges Update, oder Bug-Exploitation) mit User-Privilegien ausgeführt wird. Read-Zugriff auf `~/.ssh/`, `~/.aws/credentials`, Browser-Cookies, lokal gespeicherte Tokens — alles direkt erreichbar.

### Remediation

Ship a Dockerfile (python slim, non-root USER 10001, no secrets in layers) and document a stdio launch via `docker run -i --rm --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges -e DISCOVER_SWISS_KEY ghcr.io/.../discover-swiss-mcp` in the Claude Desktop config; alternatively document uvx-based isolation as the minimum and mark container use as recommended.

**Disposition:** No container is shipped; the server runs as a local stdio process of the user. If a container image is ever published, it gets non-root, read-only FS and dropped capabilities in the same PR.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-007` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
