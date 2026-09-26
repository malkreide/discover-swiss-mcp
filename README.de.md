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

**Pre-Release — Bestätigung der Search-Berechtigung durch discover.swiss: ausstehend (pending).**

| Punkt | Stand |
|---|---|
| Search-Berechtigung (schriftliche Bestätigung durch discover.swiss) | **pending** — Release-Gate |
| Tools | alle acht registriert (P3), Live-Canaries vorhanden (P4) |
| Release | keines; Version 0.1.0 ist nicht publiziert |

Die Live-Probe vom 17.09.2026 hat gezeigt, dass `/search` für den Open-Zugang
funktioniert — Volltext, Distanz-Ranking, Datumsfilter, 31 Facetten —, obwohl
die offizielle Doku das Gegenteil behauptet («You can't use the search
functionality»). Der ganze Server steht auf diesem Endpoint, und genau das
macht den Widerspruch zum Hauptrisiko: Eine Berechtigung, die der Doku
widerspricht, kann ohne Ankündigung entzogen werden.

- Die schriftliche Bestätigung durch discover.swiss ist ein **Release-Gate**.
  Kein Release, bevor dieses Gespräch stattgefunden hat. Danach
  `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED=JJJJ-MM-TT` setzen; dieser Abschnitt
  wechselt dann von *pending* auf *confirmed* mit diesem Datum.
- `source_status` meldet denselben Stand zur Laufzeit, damit ein Host ihn
  sieht, ohne diese Datei zu lesen.
- Wird die Berechtigung entzogen, antwortet der Server über einen schmaleren
  Listen-Fallback weiter (siehe *Architektur-Entscheid*).

---

## Anker-Abfragen

Drei Fragen, für die dieser Server gebaut ist — gewählt nach der Abdeckung, die
er tatsächlich hat. Die Tool-Kette zu jeder — welches Tool, in welcher
Reihenfolge, mit welchen Parametern — steht in [docs/DEMO.md](docs/DEMO.md),
für alle mit einem Key reproduzierbar.

1. **Stadt (Zürich-Pilot)** — *«Ich habe einen Regentag in Zürich — welche
   Museen sind in Gehdistanz zum HB, und wo esse ich danach vegetarisch?»*
   `search` → `get_details` → `search`; Zürich Tourismus als Quelle
   (CC BY-SA), Attribution sichtbar.
2. **Outdoor (Glarnerland)** — *«Ich bin in Braunwald: Welche Wanderungen mit
   wenig Höhenmetern gibt es, wie sieht es gerade auf der Webcam aus, und ist
   etwas gesperrt?»* `find_tours` → `webcams_near`, zusammen mit
   `swiss-tourism-mcp` (Sperrungen, Bergbahnen) und `meteoswiss-mcp` (Wetter).
   Zeigt zwei Server im Zusammenspiel.
3. **Unterkunft (national)** — *«Family-friendly hotel near Interlaken, three
   stars, accessible — and how do I get there from Zurich airport?»*
   `find_accommodation` mit Distanz-Ranking → `get_details`, danach
   `swiss-transport-mcp` für die Anreise.

---

## Scope-Karte

Was der offene Index enthält, live gezählt am **17.09.2026**
(`probes/PROBE_REPORT_discover-swiss-mcp.md`). Insgesamt 20'817 Objekte.

| Drin | Anzahl | Bemerkung |
|---|---:|---|
| Beherbergungsbetriebe, **national** | 5'275 | Zermatt bis Genf; HotellerieSuisse, Schweiz Tourismus, TOMAS, contentdesk |
| Hotelzimmer und Besprechungsräume | 10'112 Zimmer | von `search` ausgeschlossen, ausser `types` verlangt sie |
| Sehenswürdigkeiten — Zürich (Zürich Tourismus) | 1'311 | Museen, Restaurants, Shops, Nachtleben |
| Sehenswürdigkeiten — Ostschweiz | 6'211 | Glarnerland 1'752 · Thurgau 1'381 · St. Gallen-Bodensee 1'338 · Heidiland 711 · Appenzellerland 608 · Toggenburg 421 |
| Liechtenstein · Engadin Scuol | 553 · 429 | |
| Touren | 223 | Ostschweiz, Region Zürich; 16 von SchweizMobil |
| Webcams | 73 | alle in der Ostschweiz |
| Skigebiete · Bergbahnen und Lifte | 21 · 36 | |

| Nicht drin | Warum das zählt |
|---|---|
| Sehenswürdigkeiten, Touren, Webcams für **Berner Oberland, Zentralschweiz, Wallis, Tessin, Romandie** | Hotels dort sind abgedeckt, Sehenswürdigkeiten, Restaurants und Wanderungen nicht. Eine leere Antwort heisst dort *keine Daten*, nicht *nichts da*. |
| **Veranstaltungen** | 21 Einträge im ganzen Index, darunter ein Testobjekt — praktisch leer. `find_events` sagt das in seiner Description. |
| **Preise pro Nacht** | Nur eine vom Anbieter deklarierte Preisspanne (Niedrig / Mittel / Hoch). |
| **Verfügbarkeit** | Nicht im Infocenter-Produkt. |
| **Buchung** | Marketplace-Produkt, nicht dieser Server. |

`explore_area` und `source_status` melden diese Abdeckung zur Laufzeit, damit
ein Modell sie prüfen kann, bevor es sucht.

---

## Funktionen

- **8 Read-only-Tools** für Suche, Detail, Unterkunft, Touren, Veranstaltungen,
  Webcams, Gebietsübersicht und Quellenstatus
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

Alle acht Tools sind read-only (`readOnlyHint: true`, `openWorldHint: true`).
Jeder Treffer trägt seine eigene Attribution; jede Antwort zählt, was sie
zurückhält (`excluded_by_license`, `excluded_test_objects`,
`excluded_by_default_types`), und erklärt eine Leermenge im `hint`.

| Tool | Quelle | Zweck |
|---|---|---|
| `search` | `POST /search` | Volltext (`match: all\|name`), Typ, Ort und Distanz (`near`, `radius_km`) über den ganzen Index; Zimmer und Besprechungsräume nur auf Anfrage |
| `get_details` | `/vertices/{id}` | Beschreibung, Preise, Barrierefreiheit, Öffnungszeiten, Ausstattung — auf ~8 KB gekürzt, HTML als Text; `no_derivatives` bei CC BY-ND |
| `find_accommodation` | Search `type=LodgingBusiness` | Sterne, Garni, Preisspanne, Ausstattung, Barrierefreiheit (Pro Infirmis / OK:GO), Distanz; keine Verfügbarkeit, keine Preise pro Nacht |
| `find_tours` | Search `type=Tour` | Art, Schwierigkeit, Länge, Aufstieg, Saisonmonat, Region, Distanz |
| `find_events` | Search `type=Event`, OData-Filter auf `schedule` | Zeitraum (Default 30 Tage); dünne Abdeckung in der Description benannt; Testobjekte und All-Rights-Reserved-Events zurückgehalten und gezählt; der Sentinel 2099 erscheint als `date_open` («Termin offen»), nie als Datum |
| `webcams_near` | Search `type=Webcam` + `geo.distance` | Radius (Default 25 km) oder Region; `live_url` fürs Livebild, `snapshot_url` als gespeichertes Standbild beschriftet |
| `explore_area` | Search mit Facetten | Zähler nach Typ, Dateninhaber, Saison, Preisspanne für Region, Ort oder Radius; Kurznamen auf OData gemappt, verworfene Namen in `missing_facets` |
| `source_status` | `/status`, Zähler, ungefilterte Facettenzählung | Erreichbarkeit, Search verfügbar, Calls pro Minute, Quota-Zustand, Indexgrösse, Abdeckung, Stand der Search-Bestätigung; funktioniert ohne Key |

Die Tool-Definitionen sind in `docs/tool-hashes.json` festgehalten; nach einer
gewollten Änderung im selben PR `python scripts/gen_tool_hashes.py --write`
ausführen.

---

## Attribution

Jede Antwort nennt ihre Anbieter, und der Host muss sie anzeigen.

Jeder Treffer trägt ein `attribution`-Objekt — Anbieter, Lizenz und den
Copyright-Vermerk des Anbieters (z. B. «Zürich Tourismus www.zuerich.com»,
CC BY-SA). Ein Resultat kann drei Lizenzen mischen: Zürich Tourismus
(CC BY-SA), SchweizMobil (CC BY), TOMAS (CC BY-ND). Eine einzelne Lizenzzeile
in einer Fusszeile deckt keinen davon korrekt ab.

- **Hosts und Assistenten:** Anbieter und Lizenz zusammen mit dem Inhalt aus
  einem Treffer anzeigen. Weitergegebene CC-BY-SA-Inhalte bleiben CC BY-SA.
- **CC BY-ND** (`no_derivatives: true`, meist TOMAS-Zimmer): zitieren oder
  Fakten nennen, die Beschreibung nie umformulieren.
- **Zurückgehaltene Objekte** (alle Rechte vorbehalten, ohne Lizenz) werden gar
  nicht ausgeliefert; `excluded_by_license` sagt, wie viele es waren.

Regeln und Whitelist stehen in [docs/LICENSES.md](docs/LICENSES.md).

---

## Architektur-Entscheid

**ARCH A — nur Live-API, Search-zentriert, mit Listen-Fallback.**
(`probes/PROBE_REPORT_discover-swiss-mcp.md`, Abschnitt 6)

- `/search` deckt Volltext, Typ, Ort, Distanz, Datum und Facetten in einem
  Endpoint ab. Sieben der acht Tools sind Sichten darauf; `/vertices/{id}`
  liefert das Detail.
- Es gibt keinen Dump zum Spiegeln, und bei 60 Calls pro Minute und 50'000 pro
  Monat genügt ein Cache: 15 Minuten für Search, 24 Stunden für Detail. Eine
  erschöpfte Monatsquota (`403` mit «quota») ist ein Zustand —
  `degraded: quota_exhausted` — und wird nie wiederholt.
- **Das Risiko ist die Berechtigung.** Search widerspricht der Doku und kann
  entzogen werden. Bei `401`/`403` auf `/search` weichen `search` und
  `find_accommodation` auf die typisierten Listen-Endpoints mit
  clientseitigem Orts- und Distanzfilter aus, antworten mit
  `provenance: list_fallback`, `degraded: search_unavailable` und sagen im
  `hint`, was sie ignoriert haben. Der Fallback ist bewusst schmal: kein
  Volltext, keine Sterne-, Preis- oder Ausstattungsfilter, höchstens acht
  Listenaufrufe pro Tool-Aufruf.
- Ein einziges Project: `dsod-content`. `dsod-hs` ist eine Teilmenge.

---

## Bekannte Einschränkungen

Die zwölf Fundstücke der Live-Probe, die das Verhalten dieses Servers prägen
(Probe-Report, Abschnitt 10; Details im [CHANGELOG.md](CHANGELOG.md)):

1. **Die Doku verneint Search, die API bejaht sie.** Release-Gate: schriftliche Bestätigung.
2. **Das Doku-Beispiel-Project `demo-web` liefert 400.** Projects kommen aus `/projects`.
3. **Paging heisst `nextPageToken`, nicht `continuation`.** Feldnamen aus Live-Antworten, nicht aus der Doku.
4. **`top=1000` heisst nicht 1000.** Cosmos DB schneidet bei ~4 MB; dem Token wird gefolgt.
5. **Open-Produkt ist nicht offene Lizenz.** All-Rights-Reserved- und lizenzlose Objekte werden zurückgehalten und gezählt.
6. **`ds-containedInPlaceFilter` ist kein Filter.** Er frisiert die Antwort; der Treffer-Filter ist der Query-Parameter.
7. **Schweiz Tourismus liefert bereits Daten** (2'769 Hotels) — der offene Kanal trägt ihre Inhalte.
8. **Falsch geschriebene Facetten-Namen werden still verworfen — ein erfundener lässt den ganzen Request mit 400 scheitern.** Nur die acht verifizierten Namen werden gesendet; alles andere steht in `missing_facets`.
9. **Ein Hotel wiegt 78 KB.** `get_details` kürzt auf ~8 KB.
10. **Testdaten im Produktivindex.** «Demo Event» wird zurückgehalten und in `excluded_test_objects` gezählt.
11. **Beschreibungen sind HTML mit Entities.** Serverseitig zu Klartext aufgelöst.
12. **Der Index ist zur Hälfte Zimmer und Besprechungsräume.** `search` schliesst sie aus, ausser sie werden verlangt.

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
| `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED` | nein | `pending` | Datum (`JJJJ-MM-TT`) der schriftlichen Search-Bestätigung durch discover.swiss; von `source_status` gemeldet |

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
│   ├── licenses.py        # Lizenz-Whitelist, Attribution, Testobjekt-Filter
│   ├── transform.py       # HTML zu Text, Kürzen der Detail-Objekte
│   ├── net.py             # SSRF-Schutz, DNS-Pinning
│   ├── client.py          # API-Client: Rate-Limit, Retries, Cache, Listen-Fallback
│   └── logging_config.py  # structlog, JSON nach stderr
├── tests/                 # Unit-Tests; test_live.py ist der `live`-Marker, nicht in der CI
├── probes/                # Live-Probe: Skripte, Rohdaten, Report
├── audits/                # Audit-Reports (mcp-audit)
├── docs/                  # LICENSES.md, DEMO.md, tool-hashes.json
└── scripts/               # Repo-Prüfung, Release-Gate, Tool-Hashes
```

---

## Tests

```bash
# Das fährt die CI — ohne Netz
pytest -m "not live"
ruff check .
ruff format --check .
python scripts/validate_repo.py .

# Live-Canaries — echte API, Key aus der Umgebung, nie in der CI
export DISCOVER_SWISS_KEY="dein-subscription-key"
pytest -m live -rA
```

Die Live-Canaries (`tests/test_live.py`, rund zwanzig Calls) halten jedes Tool
an etwa der Hälfte dessen fest, was der Index am 17.09.2026 enthielt —
«Landesmuseum» ≥ 20 Treffer, Hotels ≥ 2'000, Webcams im Umkreis von 100 km um
St. Gallen ≥ 30 usw. — und prüfen, dass Scope-Parameter greifen:
`match="name"` verengt, `containedInPlace/id` kommt als Facette zurück, die
Landesmuseum-Beschreibung kommt ohne HTML-Entities, das nächste Hotel bei
Interlaken liegt in Interlaken. Eine unterschrittene Untergrenze heisst: Ein
Tool findet nicht mehr, was da ist. Ohne Key überspringt das Modul; ein Skip
ist kein Bestehen.

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
