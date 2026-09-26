## Finding: SEC-016 — 0.0.0.0-Binding-Prevention (NeighborJack)

| Feld | Wert |
|---|---|
| **Severity** | critical |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — vor dem Release zu beheben |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-016` |
| **PDF-Reference** | Sec 4 (Empirie 2025) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Non-loopback bind is silent: the 0.0.0.0 run logged no warning (only the lifespan INFO event carrying host=0.0.0.0), and there is no host allow-list to compensate (criterion 7 unmet)
- README does not explain the local vs container differentiation or warn against 0.0.0.0 outside containers (criterion 6 unmet)
- No deployment configuration exists in which an explicit 0.0.0.0 would live (criterion 5 not demonstrable; server is local-only)

### Expected Behavior

- [ ] Im Code ist **kein** `0.0.0.0`-Binding als Default hardcoded
- [ ] Die Bind-Adresse ist **konfigurierbar** — Environment-Variable *oder* CLI-Flag; der Mechanismus ist frei
- [ ] Der Default ist **Loopback** (`127.0.0.1`)
- [ ] Der gesetzte Wert **erreicht den Listener**: er wird an *jeden* Pfad durchgereicht, der die App oder den Server baut, und ein Lauf mit gesetztem Wert zeigt ihn im Startlog (Modus 3)
- [ ] `0.0.0.0` steht **explizit in der Deployment-Konfiguration** — Dockerfile, `railway.toml`, Compose-File oder Start-Kommando —, nicht im Code
- [ ] README erklärt die Differenzierung lokal/container
- [ ] Ein Bind ausserhalb Loopback ist **nicht still**: Wenn keine eingehende Host-Allow-List ihn kompensiert, sagt eine Startwarnung, dass der Server jetzt im Netz steht

### Warum die Kriterien die Eigenschaft nennen und nicht den Mechanismus

Bis v1.4.x verlangte Kriterium 2 wörtlich «via **Environment-Variable**». Das misst die Bauform statt der Sache. `zurich-opendata-mcp` löst dieselbe Aufgabe mit `--host` und Default `127.0.0.1` — Absicht vollständig erfüllt, Kriterium wörtlich verfehlt. Ein Check, der so gelesen wird, erzeugt ein Finding gegen eine korrekte Implementierung und lädt zur Gegenrichtung ein: eine `MCP_HOST`-Variable nachzurüsten, die niemand liest, damit die Zeile grün wird.

**Der Mechanismus ist nicht der Punkt — das Durchreichen ist es.** Vor `0.7.0` hatte derselbe Server gar keine Konfigurationsfläche: `mcp.run(transport="streamable-http", port=…)` ohne `host=`, uvicorn band immer `127.0.0.1`, und es gab kein Flag, das daran etwas geändert hätte. Ein Kriterium der Form «es existiert eine Env-Var» hätte diesen Zustand angezeigt, aber den Folgefehler nicht: dass eine vorhandene Option den Listener nicht erreicht. Deshalb steht die Wirkung im Kriterium und wird in Modus 3 gemessen, nicht die Herkunft des Wertes.

### Abgrenzung der Startwarnung gegen `SEC-024`

Kriterium 7 war bis v1.4.x als «Optional» geführt. Es ist keines: Alle drei Portfolio-Server, aus denen die Belege stammen, warnen beim Nicht-Loopback-Bind. Was sie **nicht** tun, ist die Container-Detection, die hier früher als Auslöser stand — die ist in keinem einzigen implementiert. Ausgelöst wird bei allen dreien durch die **fehlende Allow-List**, und deshalb ist das Kriterium so formuliert.

Damit kann **dieselbe Logzeile** zwei Checks bedienen, und die Frage, ob das eine Doppelung ist, gehört beantwortet: Nein, aber knapp. `SEC-024` fragt, ob die *Abwesenheit der Allow-List* angesagt wird — Subjekt ist die Allow-List. Hier ist das Subjekt die **Exposition**: dass der Server das Loopback verlassen hat. Zwei Server können deshalb hier bestehen und dort durchfallen (`0.0.0.0` mit Allow-List, kein Wort im Log) und umgekehrt. Wer die Zeile entfernt, verletzt beide — das ist kein Doppelbefund, sondern eine Ursache mit zwei Wirkungen.

Der vollere Fall ist trotzdem besser und in `bag-health-mcp` gebaut: Warnung ohne Allow-List, `INFO` **mit** Allow-List. Dann ist der Bind nie still, auch nicht im sauber konfigurierten Deployment. Gefordert ist er nicht — wer die Allow-List setzt, hat die Exposition erkennbar entschieden.

### Evidence

- src/discover_swiss_mcp/config.py:49 — Settings.host default '127.0.0.1'; config.py:129 — DISCOVER_SWISS_MCP_HOST env var, default '127.0.0.1'
- src/discover_swiss_mcp/server.py:364-368 — settings.host passed both to mcp.streamable_http_app(host=…) and to uvicorn.run(host=…); the only network path
- repo — grep for 0.0.0.0 host defaults in src/ and config files finds none (only net.py:42 '0.0.0.0/8' in the egress blocklist)
- runtime (audit): default run → 'Uvicorn running on http://127.0.0.1:18766'; with DISCOVER_SWISS_MCP_HOST=0.0.0.0 → 'Uvicorn running on http://0.0.0.0:18767' (value reaches the listener)
- README.md:142 and README.md:247 — default bind 127.0.0.1 documented, DISCOVER_SWISS_MCP_HOST listed

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/config.py:49 — Settings.host default '127.0.0.1'; config.py:129 — DISCOVER_SWISS_MCP_HOST env var, default '127.0.0.1'
- src/discover_swiss_mcp/server.py:364-368 — settings.host passed both to mcp.streamable_http_app(host=…) and to uvicorn.run(host=…); the only network path
- repo — grep for 0.0.0.0 host defaults in src/ and config files finds none (only net.py:42 '0.0.0.0/8' in the egress blocklist)
- runtime (audit): default run → 'Uvicorn running on http://127.0.0.1:18766'; with DISCOVER_SWISS_MCP_HOST=0.0.0.0 → 'Uvicorn running on http://0.0.0.0:18767' (value reaches the listener)
- README.md:142 and README.md:247 — default bind 127.0.0.1 documented, DISCOVER_SWISS_MCP_HOST listed

**Geschlossen**
- Loopback default, configurable bind and propagation to both the app builder and the listener are verified by two start-log runs. The silent non-loopback bind is the substantive gap; combined with SEC-024 a 0.0.0.0 bind exposes an unauthenticated, host-unchecked endpoint without any log signal. Not critical because it requires an explicit operator opt-in.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Die empirische Untersuchung von 2025 ergab: ein erheblicher Teil der OSS-MCP-Server bindet ihren HTTP-Listener an `0.0.0.0` (alle Interfaces) und vertraut implizit darauf, dass Firewall-Regeln den Zugang beschränken. Auf einem Entwickler-Laptop in einem öffentlichen WLAN, einem Co-Working-Space oder einer Konferenz wird der lokale MCP-Server damit für **alle** Geräte im selben Subnetz erreichbar.

### Remediation

In main(): if settings.host not in ('127.0.0.1','localhost','::1') and no host allow-list is configured, log a WARNING naming the exposure; add a README 'Network binding' paragraph (loopback default; 0.0.0.0 only in containers, together with an allow-list).

**Disposition:** A 0.0.0.0 bind is silent. Refuse a non-loopback bind unless DISCOVER_SWISS_MCP_ALLOW_REMOTE=1 is set, and log a warning when it is.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-016` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
