# PROBE_OPEN — die offenen Fragen aus STOP-GATE P1

Datum: 2026-09-23 · Project `dsod-content` · Basis `https://api.discover.swiss/info/v2`

## (1) `containedInPlace` als Query-Parameter auf Listen-Endpoints

Gegenprobe ist die Search-Seite, wo der Filter verifiziert ist. Stimmen Listen- und Search-Zahl überein, filtert der Parameter; bleibt die Listenzahl auf dem Gesamtbestand, wird er still ignoriert.

| Endpoint | Gebiet | Bestand gesamt | Liste gefiltert | Search gefiltert | Unsinns-ID | Befund |
|---|---|---:|---:|---:|---:|---|
| _Auflösung_ | «Glarnerland» → `ds_glarnerland` | | | | | Facette: Schweiz=osm_51701 (351), Glarnerland=ds_glarnerland (345), Glarus=osm_1685673 (338), Glarner Alpen=osm_11342352 (327) |
| _Auflösung_ | «Zürich» → `osm_1690227` | | | | | Facette: Schweiz=osm_51701 (1073), Zürich=osm_1690227 (894), Kinderregion=ds_kire (878), Zürich=kire_zurich (785) |
| `/tours` | Glarnerland (`ds_glarnerland`) | 223 | 117 | 117 | 0 | ✅ filtert, Zahl deckt sich mit der Search-Seite |
| `/civicStructures` | Zürich (`osm_1690227`) | 1406 | 232 | 232 | 0 | ✅ filtert, Zahl deckt sich mit der Search-Seite |

## (2) Zusatzfelder im Listen-`select`

Basis (P1, belegt): `identifier,name,type,additionalType,license,copyrightNotice,dataGovernance,geo,containedInPlace`

| Endpoint | alle Kandidaten zusammen | erlaubt | abgelehnt |
|---|---|---|---|
| `/lodgingbusinesses` | HTTP 200 | `address`, `url`, `link`, `image`, `lastModified`, `telephone` | — |
| | _in der Antwort tatsächlich vorhanden_ | address, image, lastModified, link, telephone, url | |
| `/civicStructures` | HTTP 200 | `address`, `url`, `link`, `image`, `lastModified`, `telephone` | — |
| | _in der Antwort tatsächlich vorhanden_ | address, image, lastModified, telephone | |
| `/webcams` | HTTP 200 | `address`, `url`, `link`, `image`, `lastModified`, `telephone` | — |
| | _in der Antwort tatsächlich vorhanden_ | image, lastModified, link | |

## (3) Feldname der Gesamtzahl bei `includeCount=true`

Gemessen: `count`. Envelope-Keys je Endpoint in `probe_open_out/envelope_*.json`.

## (4) Der echte 429-Body

Nicht gemessen — `--rate-limit` war nicht gesetzt.

## Konsequenzen für P2

- (1) ✅ → `list_fallback()` bleibt wie gebaut, `containedInPlace` ist der Gebietsfilter.
- (1) ❌ → `list_fallback()` verliert den Gebietsparameter; der Fallback filtert nur noch clientseitig über `geo`, und die Tool-Description muss sagen, dass ohne Koordinate keine Regionsabgrenzung möglich ist.
- (2) → erlaubte Felder in `LIST_SELECT` (client.py) übernehmen, abgelehnte dort als gemessen-verboten kommentieren.
- (3) → `_total_from()` kann auf den gemessenen Namen zeigen; tolerant bleibt es trotzdem.
- (4) → falls die Regex nicht greift, `_retry_after_seconds()` auf den echten Wortlaut ziehen.


---

13 Calls. Rohantworten in `probe_open_out/`.

