> 🇨🇭 **Teil des [Swiss Public Data MCP Portfolios](https://github.com/malkreide)**

# discover-swiss-mcp

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io/)
[![Key erforderlich](https://img.shields.io/badge/auth-bring%20your%20own%20key-orange)](https://portal.discover.swiss/)

> MCP-Server für discover.swiss Infocenter Open — Schweizer Tourismusdaten durchsuchen, mit Attribution pro Objekt

🇬🇧 [English Version](README.md)

---

## Status

**pre-release — search entitlement confirmation from discover.swiss pending.**

Die Live-Probe vom 17.09.2026 hat gezeigt, dass `/search` für den Open-Zugang
funktioniert — Volltext, Distanz-Ranking, Datumsfilter, 31 Facetten —, obwohl
die offizielle Doku das Gegenteil behauptet («You can't use the search
functionality»). Der ganze Server steht auf diesem Endpoint, und genau das
macht den Widerspruch zum Hauptrisiko: Eine Berechtigung, die der Doku
widerspricht, kann ohne Ankündigung entzogen werden.

Zwei Konsequenzen, beide bereits entschieden:

- Die schriftliche Bestätigung durch discover.swiss ist ein **Release-Gate**.
  Kein Release, bevor dieses Gespräch stattgefunden hat.
- Der Server trägt einen Fallback. Bei `401`/`403` auf `/search` weicht er auf
  die Listen-Endpoints mit Gebietsfilter (`containedInPlace`) und
  clientseitiger Distanzberechnung aus und kennzeichnet die Antwort als
  `provenance: list_fallback`. Der Fallback ist bewusst schmal — kein Volltext.

Stand: **P2** — vier der acht Tools sind registriert (`search`,
`get_details`, `find_accommodation`, `find_tours`); die übrigen vier folgen in
P3.

---

## Übersicht

`discover-swiss-mcp` öffnet KI-Assistenten den offenen Index von
[discover.swiss](https://discover.swiss/) — 20'817 Objekte Schweizer
Tourismusdaten in schema.org-Form, mit Lizenz und Attribution an jedem
einzelnen Objekt.

Die Abdeckung ist ungleich, und wer das weiss, nutzt die Daten besser:

| Bereich | Abdeckung | Detail |
|---|---|---|
| Unterkünfte | **national** | 5'275 Betriebe, 10'112 Zimmer — Zermatt bis Genf |
| Sehenswürdigkeiten | **regional** | Zürich (1'311), Ostschweiz-Partner, Liechtenstein, Engadin Scuol |
| Touren, Webcams, Skigebiete | regional | 223 Touren, 73 Webcams, 21 Skigebiete |
| Veranstaltungen | **fast leer** | 21 Einträge, darunter Testobjekte |

Für Berner Oberland, Zentralschweiz, Wallis, Tessin und Romandie gibt es keine
POI-Inhalte. Ein Tool, das das verschweigt, liefert eine selbstsichere Antwort
über eine Region, zu der es keine Daten hat.

**Anker-Abfrage:** *«Ich habe einen Regentag in Zürich — welche Museen sind in
Gehdistanz zum HB, und wo esse ich danach vegetarisch?»*

---

## Funktionen

- **8 Read-only-Tools** für Suche, Detail, Unterkunft, Touren, Veranstaltungen,
  Webcams und Gebietsübersicht — vier verfügbar, vier geplant für P3
- **Attribution pro Objekt** — Anbieter, Lizenz und Copyright-Vermerk stehen in
  der Response, nicht in diesem README
- **Lizenz-Whitelist** auf dem root-`license`-Feld; alles andere wird in
  `excluded_by_license` gezählt und nie ausgeliefert
- **Leermengen tragen einen Grund** — ein `hint`, der sagt, was zu ändern ist,
  nie eine unkommentierte leere Liste
- **Degradierte Zustände sind benannt** — `quota_exhausted`,
  `upstream_unreachable`, `search_unavailable`
- **Zwei Transporte** — stdio (Claude Desktop) und Streamable HTTP (Cloud)

---

## Voraussetzungen

- Python 3.11, 3.12 oder 3.13
- Ein discover.swiss-Infocenter-Open-Subscription-Key (Self-Service auf
  [portal.discover.swiss](https://portal.discover.swiss/)) — bring your own key
- Rate-Limits dieses Zugangs: 60 Calls/Minute, 50'000 Calls/Monat

---

## Installation

```bash
git clone https://github.com/malkreide/discover-swiss-mcp.git
cd discover-swiss-mcp
pip install -e ".[dev]"
```

---

## Verwendung / Schnellstart

```bash
export DISCOVER_SWISS_KEY="dein-subscription-key"

# stdio (Claude Desktop und andere lokale Clients)
python -m discover_swiss_mcp

# Streamable HTTP — bindet standardmässig an 127.0.0.1:8000 (nur localhost)
DISCOVER_SWISS_MCP_TRANSPORT=streamable-http python -m discover_swiss_mcp
```

Der Key wird ausschliesslich aus der Umgebung gelesen. Er wird als Secret
gehalten, erscheint in keiner Log-Zeile und gehört in keine Datei, die
committet wird.

---

## Verfügbare Tools

<!-- Namen exakt so, wie sie registriert sind — nicht die Funktionsnamen. -->

Die acht Tools aus dem Probe-Report, Abschnitt 7. Alle sind read-only
(`readOnlyHint: true`, `openWorldHint: true`). Jeder Treffer trägt seine eigene
Attribution; jede Antwort zählt, was sie zurückhält (`excluded_by_license`,
`excluded_test_objects`, `excluded_by_default_types`), und erklärt eine
Leermenge im `hint`.

| Tool | Stand | Quelle | Zweck |
|---|---|---|---|
| `search` | verfügbar | `POST /search` | Volltext (`match: all\|name`), Typ, Ort und Distanz (`near`, `radius_km`) über den ganzen Index; Zimmer und Besprechungsräume nur auf Anfrage |
| `get_details` | verfügbar | `/vertices/{id}` | Beschreibung, Preise, Barrierefreiheit, Öffnungszeiten, Ausstattung — auf ~8 KB gekürzt, HTML als Text; `no_derivatives` bei CC BY-ND |
| `find_accommodation` | verfügbar | Search `type=LodgingBusiness` | Sterne, Garni, Preisspanne, Ausstattung, Barrierefreiheit (Pro Infirmis / OK:GO), Distanz; keine Verfügbarkeit, keine Preise pro Nacht |
| `find_tours` | verfügbar | Search `type=Tour` | Art, Schwierigkeit, Länge, Aufstieg, Saisonmonat, Region, Distanz |
| `find_events` | P3 | Search `type=Event` | Dünne Abdeckung als Scope benannt; Testobjekte gefiltert und gezählt |
| `webcams_near` | P3 | Search `type=Webcam` | Link aufs Livebild plus letzter Snapshot, so beschriftet |
| `explore_area` | P3 | Search mit Facetten | Welche Angebote es in einer Region gibt; fehlende Facetten werden gemeldet |
| `source_status` | P3 | `/status` und Zähler | Erreichbarkeit, Quota-Rest, ob Search verfügbar ist |

Die Tool-Definitionen sind in `docs/tool-hashes.json` festgehalten; nach einer
gewollten Änderung im selben PR `python scripts/gen_tool_hashes.py --write`
ausführen.

---

## Konfiguration

| Variable | Pflicht | Default | Zweck |
|---|---|---|---|
| `DISCOVER_SWISS_KEY` | ja | — | Subscription-Key, gesendet als `Ocp-Apim-Subscription-Key` |
| `DISCOVER_SWISS_PROJECT` | nein | `dsod-content` | Abgefragtes Project; `dsod-hs` ist eine Teilmenge |
| `DISCOVER_SWISS_MCP_TRANSPORT` | nein | `stdio` | `stdio` oder `streamable-http` |
| `DISCOVER_SWISS_MCP_HOST` | nein | `127.0.0.1` | Bind-Adresse für den HTTP-Transport |
| `DISCOVER_SWISS_MCP_PORT` | nein | `8000` | TCP-Port für den HTTP-Transport |
| `DISCOVER_SWISS_MCP_LOG_LEVEL` | nein | `INFO` | structlog-Level; JSON geht nach stderr |

Datenlizenzen und Attributionsregeln stehen in
[docs/LICENSES.md](docs/LICENSES.md).

---

## Projektstruktur

```
discover-swiss-mcp/
├── src/discover_swiss_mcp/
│   ├── __main__.py        # python -m Einstieg, Transport aus der Umgebung
│   ├── server.py          # MCP-Server, Lifespan, Tool-Wrapper
│   ├── tools.py           # die *_impl-Funktionen, Ein- und Ausgabemodelle
│   ├── config.py          # Settings aus ENV; der Key ist ein SecretStr
│   ├── models.py          # der Response-Envelope
│   ├── client.py          # API-Client — Stub mit P1-Markern
│   └── logging_config.py  # structlog, JSON nach stderr
├── tests/                 # Unit-Tests; der `live`-Marker läuft nicht in der CI
├── probes/                # Live-Probe: Skripte, Rohdaten, Report
├── docs/LICENSES.md       # Lizenz-Whitelist und Attributionsregeln
└── scripts/               # Repo-Prüfung und Release-Gate
```

---

## Tests

```bash
# Das fährt die CI — ohne Netz
pytest -m "not live"

ruff check .
ruff format --check .
```

Unit-Tests laufen offline. Mit `live` markierte Tests gehen an die echte API
und brauchen einen Subscription-Key; die CI führt sie nie aus.

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md)

---

## Mitwirken

Beiträge sind willkommen — siehe [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Sicherheit

Schwachstellen bitte wie in [SECURITY.md](SECURITY.md) beschrieben melden.

---

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE)

Die **Software** ist MIT. Die **Daten** sind es nicht: Sie bleiben unter der
Lizenz des Anbieters, der an jedem Treffer genannt ist. Siehe
[docs/LICENSES.md](docs/LICENSES.md).

---

## Autor

Hayal Oezkan · [malkreide](https://github.com/malkreide)

---

## Credits & Verwandte Projekte

- **Daten:** [discover.swiss](https://discover.swiss/) Infocenter Open — Daten der je Objekt genannten Anbieter
- **Protokoll:** [Model Context Protocol](https://modelcontextprotocol.io/) — Anthropic / Linux Foundation
- **Konventionen:** [openlex-mcp](https://github.com/malkreide/openlex-mcp) — Referenzimplementation dieses Portfolios
- **Portfolio:** [Swiss Public Data MCP Portfolio](https://github.com/malkreide)
