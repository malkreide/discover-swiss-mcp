# Nachprüfung nach P5 — discover-swiss-mcp

Lauf `2026-09-26T121656-Z-discover-swiss-mcp` · Ziel `f326260` (P5, Branch `claude/new-session-52dokz`) · Skill mcp-audit 2.3.0 · Katalog-Hash `2bbded90…d3ecf` (gleich wie im Erstaudit)

## Was geprüft wurde — und was nicht

**Gezielt, kein Vollaudit.** Geprüft wurden die 27 Checks, die P5 adressiert hat: die drei Blocker `SEC-003`, `SEC-007`, `SEC-021` und die 20 als «vor Release» eingestuften Befunde, dazu `FID-L02`, `FID-L03`, `ARCH-013`, `ARCH-022`. Die übrigen 62 Checks des Erstaudits (`AUDIT_2026-09-26.md`) wurden nicht erneut gelaufen; ihre Ergebnisse gelten für `bd0e371`, nicht für `f326260`.

Zwei Prüf-Agenten nach Themen (Sicherheit/Identität: 13 Checks; Datentreue/Betrieb: 14 Checks), jeder Lauf durch `verify_raw_outputs.py` und `agent_run_log.py` gegated — beide `ok`, keine Wiederholung. Rohdaten: `raw/*.txt`, jeweils mit `previous_status`, `previous_gaps_closed` und `previous_gaps_open`.

## Ergebnis

| | pass | partial | fail |
|---|---:|---:|---:|
| Erstaudit (`bd0e371`), diese 27 Checks | 0 | 15 | 12 |
| Nachprüfung (`f326260`) | 10 | 16 | 1 |

**Die drei Blocker sind geschlossen:** `SEC-003`, `SEC-007`, `SEC-021` — alle `pass`.

**Gemessen bestanden:** `SEC-003`, `SEC-004`, `SEC-007`, `SEC-016`, `SEC-021`, `ARCH-013`, `ARCH-022`, `DEP-001`, `FID-L02`, `FID-L03`.

**Nicht bestanden:** `FID-005` — die Beschreibung von `search` nannte die Abfragesyntax «ungetestet», statt sie zu messen; die Probe lag vor, war aber nicht gelaufen.

## Regressionen, die P5 eingeführt hatte

Die Nachprüfung fand fünf Fehler, die erst mit den P5-Korrekturen entstanden sind. Alle fünf sind im Folge-Commit behoben und je mit einem Gegentest belegt (CONTRIBUTING, «Counter-tests»):

1. **Ausfall des Autorisierungsservers als «ungültiges Token» gecacht** (`SEC-002`, `SEC-028`): Ein DNS- oder Verbindungsfehler bei der Introspektion ergab `None`, 60 s gecacht — ein gültiges Token war eine Minute lang gesperrt, und der Client wurde zur Neu-Autorisierung geschickt. Jetzt: 503 `temporarily_unavailable`, `Retry-After: 10`, nichts gecacht.
2. **Client-Secret in `repr(AuthConfig)`** (`ARCH-005`, Kriterium 4). Jetzt ausserhalb des `repr`.
3. **Metadaten vor der Host-Prüfung** (`SEC-024`): `Host: evil.example` bekam das Metadaten-Dokument mit 200. Jetzt 421 vor jeder Antwort.
4. **Budget nach der Wartezeit der Ratenbremse nicht nachgerechnet** (`ARCH-014`, `OPS-010`): Die Anfrage nach einer Bucket-Wartezeit erhielt den Rest von *vor* der Wartezeit — bis etwa 2 × 25 s pro Aufruf. Nur unter echter Zeit sichtbar; der Test mit Kunstuhr konnte es nicht sehen.
5. **Verschachtelte Zeilen als «Lizenz vorenthalten» gemeldet** (`FID-006`): Zeilen eine Ebene tiefer fielen alle durch den Lizenzfilter. Jetzt `upstream_shape_changed`, sobald keine Zeile ein `identifier` trägt.

Dazu drei Lücken, die im selben Zug geschlossen wurden: `iss` ist Pflicht (`SEC-002` Kriterium 5), die Identität des Aufrufers wird pro Aufruf protokolliert (Kriterium 4), `ALLOWED_ORIGINS` verweigert Wildcards (`SEC-024` Kriterium 6). Die überlebende Mutation M20 (`Retry-After` als Header) hat ihren Test. Der Retry-Paar-Test für `SEC-028` fehlt nicht mehr.

`FID-005`: Die Probe ist gelaufen (Maintainer, 2026-09-26), Bericht `probes/PROBE_QUERY_discover-swiss.md`. Beschreibung, Feldbeschreibung und `hint` nennen die gemessenen Regeln; ein Live-Canary hält sie.

**Diese Folgekorrekturen sind getestet, nicht nachauditiert.** Der Status in der Tabelle unten ist der des Laufs gegen `f326260`.

## Offen — mit Begründung

| Check | Status | Offen |
|---|---|---|
| `SEC-002` | partial | HTTP auf Loopback ohne eingehende Authentisierung (Designentscheid, lokales Profil). Der Verifier-Client wird beim Herunterfahren nicht geschlossen (gering). |
| `SEC-024` | partial | Mit gesetzter `ALLOWED_HOSTS` wird Loopback nicht ergänzt — ein Host-basierter Health-Check auf 127.0.0.1 bekäme 421 (die k8s-Probes sind TCP, heute kein Bruch). |
| `ARCH-005` | partial | Settings von Hand aus `os.environ` statt `pydantic-settings` (vom Check als «o. ä.» akzeptiert). |
| `ARCH-012` | partial | Das SDK beantwortet ältere Protokollversionen (2024-11-05 bis 2025-11-25), `server/discover` nennt nur 2026-07-28. CHANGELOG und README nennen die Spec-Version nicht. |
| `ARCH-014` | partial | Budget pro HTTP-Aufruf, nicht pro Tool-Aufruf (Regionsauflösung, Listen-Fallback). Kein Jitter (bewusst). 503 ignoriert `Retry-After`; HTTP-Datum nicht geparst. |
| `ARCH-016` | partial | Kein Test gegen `server/discover`; die SDK-Defaults melden Prompts/Resources-Capabilities, die der Server nicht hat. |
| `DRIFT-002` | partial | `_schedule_entry` kann ein anderes Vorkommen als das passende melden; `WebLink` als Livebild unbelegt. |
| `DRIFT-004` | partial | `status()` trennt 404 (Endpunkt weg) nicht von 5xx. Kein geplanter Live-Lauf (`DRIFT-005` akzeptiert). |
| `FID-001` | partial | Recall-Delta für Listen-`project` und für die Facetten-Schnitte (30/20) nicht gemessen; `explore_area` meldet eine volle Facette nicht. |
| `FID-003` | partial | Transportfehler enden als Ergebnis mit `degraded`, nicht im Fehlerkanal — bewusst, der Check zählt es trotzdem. |
| `FID-006` | partial | Fehlermeldungen nennen die angekommenen Keys nicht immer; Facetten-Innenform (`values`) ungeprüft. |
| `IDENT-002` | partial | Der Versionstest überspringt einen blossen Checkout nicht. |
| `OPS-001` | partial | Kein separater Live-Workflow, kein Test-Key (Bring-your-own-Key; `DRIFT-005` akzeptiert). |
| `OPS-003` | partial | P1–P5 sind Bau-Meilensteine, nicht die Architektur-Phasen, die der Check meint. |
| `OPS-010` | partial | Geschlossen im Folge-Commit (Überlebende jetzt verzeichnet, Budget-Gegentest unter echter Zeit); nicht nachauditiert. |

## Live-Evidenz

Die Sandbox erreicht `api.discover.swiss` nicht (DNS-Pinning umgeht den Proxy). Live-Evidenz sind die Läufe des Maintainers vom 2026-09-26, Windows, Python 3.14.7: `pytest -m live -rA` 24 bestanden, 1 übersprungen (`live-evidence-2026-09-26.md`), und `probes/probe_query_syntax.py` (`probes/probe_query_out/results.json`, aus der Konsolenausgabe übertragen).

## Abweichungen vom Verfahren

- **Gezielter Umfang** statt Vollaudit, siehe oben.
- **`--skip-target-check`** bei `verify_raw_outputs.py`: Das Lauf-Verzeichnis liegt im Repo und macht den Worktree «dirty»; HEAD war `f326260` (bei `audit_init.py`: `target_dirty: false`).
- **Agent 2 hat die `SEC-*`-Dateien von Agent 1 neu geschrieben** und gab an, sie seien byte-identisch. Nicht vorgesehen: Jeder Agent schreibt nur seine eigenen IDs. Der Report-Autor hat die `SEC-*`-Befunde gegen den Code nachgelesen (Regressionen 1–3 reproduziert); gezählt wird der Inhalt, nicht die Zusicherung.
- **Python 3.14.7** beim Live-Lauf liegt ausserhalb der deklarierten Matrix 3.11–3.13; CI prüft 3.14 nicht.
