# PROBE_REPORT — discover-swiss-mcp

**Probe-Daten:** 17.09.2026, vier Läufe (44 / 48 / 156 / 52 Calls) gegen PROD `https://api.discover.swiss/info/v2`
**Produkt:** Infocenter Open (Self-Service-Key, Subscription `discover-swiss-mcp`) · **Spec:** Infocenter-PROD-V2 `20260910.2_release`
**Status:** Schritt 1 abgeschlossen inkl. Restprobe (Detail, select, Paging, Facetten, Ground Truth) · Schritt 2 getroffen · offen: Bestätigung der Search-Berechtigung durch discover.swiss

---

## 0. Kernbefund in drei Sätzen

1. Der Open-Key liefert zwei Projects (`dsod-content`, `dsod-hs`); `dsod-content` ist die Obermenge und genügt.
2. **`/search` funktioniert für den Open-Zugang** — Volltext, Distanz-Ranking ab Koordinate, Datumsfilter für Events, 31 Facetten — obwohl die Doku das Gegenteil behauptet. Das ist die Grundlage des Servers, und gleichzeitig sein grösstes Risiko (Abschnitt 6).
3. Der Index umfasst **20'817 Objekte**. **National bei Unterkünften** (5'275 Betriebe, 10'112 Zimmer, Zermatt bis Genf), **regional bei POIs**: Zürich Tourismus (1'311 Objekte: Museen, Restaurants, Shops) plus die Ostschweiz-Partner (VISIT Glarnerland 1'752, Thurgau 1'381, St. Gallen-Bodensee 1'338, Heidiland 711, Appenzellerland 608, Toggenburg 421), Liechtenstein (553) und Engadin Scuol (429): Attraktionen, Restaurants, Touren, Webcams, Skigebiete, Bergbahnen, Feuerstellen, Spielplätze. Kein POI-Inhalt aus Berner Oberland, Zentralschweiz, Wallis, Tessin, Romandie. Events sind mit 21 Einträgen praktisch leer — und enthalten Testdaten.

---

## 1. Projects und Project-Parameter

| Project | Name | Rolle |
|---|---|---|
| `dsod-content` | discover.swiss OpenData – Content | **Hauptprojekt**, alle Typen |
| `dsod-hs` | discover.swiss OpenData – HotellerieSuisse Dataset | Teilmenge (4'476 Hotels, 8'591 Zimmer, 78 Hotelgruppen) |

| Variante | HTTP | Befund |
|---|---|---|
| ohne `project` | 200 | funktioniert — Partner-Default, **nicht dokumentiert** → Server sendet immer explizit (1.2b) |
| `project=dsod-content` | 200 | |
| `project=demo-web` (Doku-Beispiel) | 400 | «Request partner doesn't match project partner» |
| `project=does-not-exist` | 400 | «Supplied project doesn't exist» |
| `/search` ohne `project` | 401 | «Project wasn't supplied or empty» — für Search ist es Pflicht |

## 2. Befund-Tabelle (Schritt 1.3) — `dsod-content`, Bestand via `includeCount=true`

| Endpoint | HTTP | Bestand | geo | Typen (Seite 1) | Provider (Seite 1) |
|---|---|---:|---|---|---|
| `/lodgingbusinesses` | 200 | **5'275** | ✅ | Hotel 64, HolidayApartment 4, B&B 1 | HotellerieSuisse 36, TOMAS 21, contentdesk 9, feratel 3 |
| `/accommodations` (Zimmer) | 200 | **10'112** | ✅ | HotelRoom 96, Apartment 4 | TOMAS 100 |
| `/localbusinesses` | 200 | 1'593 | ✅ | SportsActivityLocation 63, Store 25, NightClub 5, PublicSwimmingPool 3, DaySpa 2 | Zürich Tourismus 100 |
| `/foodEstablishments` | 200 | 1'438 | ✅ | Restaurant 80, Café 9, Winery 7, Bar 4 | Zürich Tourismus 99 |
| `/civicStructures` | 200 | 1'407 | ✅ | Museum 70, Theater 15, ArtObject 6, TouristAttraction 3 | Zürich Tourismus 98 |
| `/places` | 200 | 448 | ✅ | LandmarkOrHistoricalBuilding 30, Lake 20, Landform 14, Waterfall 7, Mountain 5 | contentdesk 80, Zürich Tourismus 20 |
| `/tours` | 200 | 223 | ✅ | Route 33, ThemeTrail 32, CrossCountry 8, TobogganRun 5, NatureTrail 4 | contentdesk 88, **SchweizMobil 12** |
| `/products` | 200 | 171 | – | Offer 96, GuestCard 2 | contentdesk 100 |
| `/webcams` | 200 | 73 | ✅ | Webcam 72 | contentdesk 73 |
| `/transportationSystems` | 200 | 36 | ✅ | CableCar 16, SkiLift 7, ChairLift 3, RackRailway 1 | contentdesk 36 |
| `/skiresorts` | 200 | 21 | ✅ | SkiResort 21 | contentdesk 21 |
| `/events` | 200 | **21** | – | Event 17, FoodEvent, MusicEvent … | contentdesk 18, Guidle 3 |
| `/imageObjects` | 200 | 33'181 | – | ImageObject | Zürich Tourismus 100 |
| `/areas` | 200 | 7'290 | ✅ | City 74, District 15, Country 5, State 3, ProtectedArea 1 | discover.swiss (OSM) |
| `/categories` · `/tags` · `/amenities` · `/awards` | 200 | 189 · 585 · 571 · 91 | – | Referenzdaten | discover.swiss, ibex fairstay |
| `/protectedAreas`, `/reviews`, `/conditions`, `/creativeWorks`, `/audio|video|mediaObjects` | 200 | **0** | – | leer im Open-Produkt | – |

Search-Facette `sourcePartner` (Hotels, CH-weit): HotellerieSuisse 3'029 · **Schweiz Tourismus 2'769** · Pro Infirmis 779 · GastroSuisse 311 · OK:GO 258 · Zürich Tourismus 160 · Engadin 111 · St. Gallen-Bodensee 81.
Search-Facette `addressLocality` (Hotels): Zürich 114 · Zermatt 108 · Genève 72 · Basel 53 · Luzern 52 · **Grindelwald 39** · Davos 36 · Ascona 35 → Unterkünfte sind national.

## 3. Lizenzen (root-`license`, Seite 1 je Endpoint)

| Endpoint | Verteilung | Konsequenz |
|---|---|---|
| lodgingbusinesses | CC BY 63, CC BY-ND 6 | frei mit Attribution |
| accommodations | **CC BY-ND 89**, CC BY 11 | ND: Beschreibungstexte nicht umformulieren → strukturierte Felder + Verweis |
| civicStructures, foodEstablishments, localbusinesses, places, tours, webcams, skiresorts, transportationSystems | CC BY-SA ≈ 100 % (Touren: 16 CC BY von SchweizMobil) | Share-Alike im README dokumentieren |
| events | CC BY-SA 18, **C-All-Rights-Reserved 3** (Guidle) | ⚠️ **nicht alles im Open-Produkt ist offen** |
| `dsod-hs` /localbusinesses (HotelGroup) | `license: None` 72 | ⚠️ ohne Lizenz = nicht offen → ausschliessen |

Jedes Objekt trägt zusätzlich `dataGovernance.origin[]` mit Datasource und Lizenz je Herkunft (z. B. `zht-cms:CC BY-SA`, `gdl:C-All-Rights-Reserved`, `osm:ODbL`) und `copyrightNotice` («Zürich Tourismus www.zuerich.com»).

**Regel für den Server:** Lizenz-Whitelist `{CC0, CC BY, CC BY-SA, CC BY-ND, ODbL}` auf root-`license`; alles andere (`None`, `C-All-Rights-Reserved`, `Unknown`, `CC BY-NC-*`) wird **nicht ausgeliefert**, sondern nur gezählt (`excluded_by_license: n`) — damit das Modell weiss, dass es etwas nicht sieht. Attribution pro Treffer aus `copyrightNotice` + Provider-Name + Lizenzkürzel.

## 4. Default-Matrix (Schritt 1.2b)

| Parameter | Weglassen bedeutet | Beleg | Server muss senden? |
|---|---|---|---|
| `top` (Listen) | ⚠️ 10 Rows | Lauf 3: 10 / 5 / 1000 | ✅ explizit; `top=1000` liefert je nach Cosmos-Page nur 460 → **immer `nextPageToken` folgen** |
| Paging-Felder | `hasNextPage` (bool) + `nextPageToken` (string) — **nicht** `continuation` wie in der Doku | raw_first_page | Feldnamen aus Live-Antwort, nicht aus Doku |
| `project` (Listen) | Partner-Default (undokumentiert) | 200 ohne project | ✅ immer `dsod-content` |
| `project` (Search) | ❌ 401 | | ✅ Pflicht als Array |
| `Accept-Language` | Default de-CH | fr/it/en übersetzen Namen («Hôtel», «Albergo», «small double room») | ✅ aus `lang` |
| `categoryVersion` | kein sichtbarer Effekt auf Listen | | `sui` setzen (Doku-Warnung Aug. 2025) |
| `select` (Listen) | ~9.5 KB/Objekt statt ~1 KB | 9'562 B vs 3'157 B bei 3 Rows | ✅ in Listen; Detail via `/vertices/{id}` |
| `datasource` | kein Filter | `zht-cms` 7'863 · `ctd-vgl` 8'692 · `chm` 0 (auf imageObjects) | optional; Provider-Filter |
| `updatedSince` | alles | `2026-09-01` → 3'435 Bilder | für Cache-Invalidierung geeignet |
| `deleted=true` | nur gelöschte | liefert andere Objekte | nie senden |
| Ordnung | stabil (zwei identische Calls, gleiche IDs) | Lauf 3 | Paging ist verlässlich |
| `ds-containedInPlaceFilter` (Header) | ⚠️ filtert die **Antwort-Property**, nicht die Treffer | Spec | Gebietsfilter = Query `containedInPlace=<id>` bzw. Search-Facette |
| `select` (Search) | Whitelist = `IndexResponse` **minus** `containedInPlace`, `context` (46 von 48) | Restprobe (b): alle 48 → 400, einzeln verifiziert | Whitelist hart codieren |
| `resultsPerPage` (Search) | Default 10; **1'000 funktioniert** (1'000 geliefert) | Restprobe (c) | explizit; Paging über `currentPage` |
| `facets[].name` | ⚠️ **unbekannte Namen werden still ignoriert** — `containedInPlace` und `ratingDifficulty` (filterPropertyName) fehlten in der Antwort, `leafType`/`sourcePartner`/`season`/`priceRange` kamen | Restprobe (d) | OData-Namen verwenden (`containedInPlace/id`, `rating/difficulty`) und Antwort-Keys gegen Anfrage prüfen (I14Y-Lektion) |
| `searchFields` | Default = alle Felder inkl. Beschreibungen: «vegetarisch» 136 (alle) vs. 0 (`name`) vs. 16 (`name,disambiguatingDescription`); «Landesmuseum» 53 / 7 / 15 | Restprobe (e) | Tool-Parameter `match: all\|name`; Tool-Description erklärt, dass `count` Erwähnungen in Beschreibungen einschliesst |

## 5. `/search` (Schritt 1.2 + 1.4 Vorstufe)

| Test | HTTP | `count` | erste Treffer |
|---|---|---:|---|
| `searchText=Landesmuseum` | 200 | 53 | Landesmuseum Zürich (CivicStructure), Liechtensteinisches Landesmuseum, Shop Landesmuseum, Erweiterungsbau … |
| `searchText=Grindelwald` | 200 | 37 | Jugendherberge Grindelwald, Bergwelt Grindelwald, Naturefriends Hostel, Downtown Lodge, Hotel Alpenblick — **nur Unterkünfte** |
| `searchText=Wanderung` | 200 | 529 | Rundwanderung Oberblegisee (Tour), Rundwanderung Braunwald … — Facette `containedInPlace`: Glarner Alpen 220, Appenzeller Alpen 102 |
| `leafType=Hotel` + `scoringReferencePoint=7.8632,46.6863` (Interlaken) | 200 | 3'093 | Hotel Du Nord, Hotel Artos, Royal St Georges, Hapimag Resort — alle Interlaken → **Distanz-Ranking funktioniert** |
| `type=Event` + `scheduleStart=heute` | 200 | 21 | mit `nextOccurrence` |
| `select` mit `leafType` | 400 | – | Select-Whitelist |
| `facets=["leafType"]` (String) | 400 | – | Facets erwarten Objekte (`FacetRequest`), Struktur aus Spec-Definition holen |
| ohne `project` | 401 | – | |

Antwort-Envelope Search: `{count, values[], facets{}}`. Facetten (31): `address/addressLocality`, `address/postalCode`, `containedInPlace/id`, `type`, `leafType`, `combinedType(Tree)`, `categoryTree`, `tag`, `sourcePartner` («Dateninhaber»), `season`, `rating/difficulty`, `rating/condition`, `length`, `elevation/ascent|descent|min|max`, `starRating/*`, `numberOfRooms|Beds`, `priceRange`, `amenityFeature`, `openingHoursSpecification/dayOfWeek`, `award`, `time`, `state`.

**Widerspruch zur Doku:** «You can't use the search functionality» (ohne Infocenter-Paket). Live: 200 mit Project. Entweder ist die Doku veraltet oder das Open-Produkt grosszügiger konfiguriert als beschrieben. → Abschnitt 6.


### 5.1 Detail-Objekte `/vertices/{id}` (Restprobe a)

| Objekt | Bytes | Felder | Was das Detail-Tool bekommt |
|---|---:|---:|---|
| Landesmuseum Zürich (CivicStructure) | 38'664 | 41 | `description` 1'634 Zeichen **als HTML mit Entities** (`<p>`, `&uuml;`), `fees` als HTML-Tabelle (Erwachsene CHF 13), `zurichcard: true` + Text, `openingHoursSpecification` (6 Tage, opens/closes), `openingDays`, `accessibility` (Pro Infirmis/ginto-Profile mit Grad und Konformität), `url`, `telephone`, `link[]` (Homepage de/en, ginto), `image.contentUrl` (zuerich.com), `photo[]` 13, `osm_id`, `availableDataLanguage` de/en/fr/it |
| Hotel Du Nord, Interlaken (LodgingBusiness) | 77'738 | 34 | `starRating` 4.0 garni, `amenityFeature` **81** Einträge, `checkinTime`/`checkoutTime`, `numberOfRooms` (61, davon 43 DZ), `numberOfBeds` 113, `paymentAccepted`, `accessibility`, `address` mit E-Mail/Telefon, `photo[]` 40 |
| RailAway Rundwanderung Oberblegisee (Tour/Route) | 18'631 | 25 | `description` HTML, `url` = SBB-Affiliate-Link, `openingHours` als Freitext **mit Jahr 2024** (veraltet), `potentialAction` ReserveAction; **keine** `length`/`elevation` (ist ein RailAway-Produkt, kein SchweizMobil-Trail) |
| «Demo Event» (Event) | 16'269 | 26 | `startDate`/`endDate`, `eventSchedule`, `eventStatus`, `location`, `organizer` — **Platzhalterdaten** («Ort», «PLZ», «Strasse 1», mail@example.ch): Testobjekt im Produktivindex |
| Webcam Atzmännig Seilpark | 6'225 | 17 | `image.contentUrl` = **Snapshot** auf media-v2.discover.swiss (nicht live), `link[]` → sky-cam.ch Livebild |
| Zur Brauerei Seerestaurant (FoodEstablishment) | 32'669 | 27 | `description` 908 Zeichen, `openingHours` Freitext, `amenityFeature`, `photo[]`, `telephone`, `url` |

**Konsequenzen:** (1) `get_details` muss **kürzen** — 78 KB pro Hotel sprengen jedes Kontextfenster: `photo[]` auf 3, `amenityFeature` auf Namen, `dataGovernance` auf Provider + Lizenz, HTML zu Text. (2) Beschreibungen sind HTML → serverseitig strippen und Entities auflösen, sonst liest das Modell `&uuml;`. (3) Freitext-`openingHours` mit altem Jahr → `disclaimer` bei Öffnungszeiten ist Pflicht, nicht Kür. (4) Testobjekte im Index → `find_events` filtert `name` ~ «Demo|Test» und Platzhalter-Adressen, meldet sie als `excluded_test_objects`. (5) Webcam-Tool liefert den `link` als Livebild, `contentUrl` nur als «letzter Snapshot».

### 5.2 Index-Zusammensetzung (Restprobe d, Facette `leafType`, 20'817 Objekte)

Hotelzimmer 5'314 · **Besprechungsraum 4'524** · Hotel 3'093 · Beherbergungsbetrieb 1'394 · Restaurant 906 · Freizeit/Dienstleistung 344 · Ort 322 · Ferienwohnung 276 · Sportanlage 216 · Geschäft 215 · Museum 202 · **Feuerstelle 176** · Bar 153 · Angebot 152 · Wohnung 141 · Ferienhaus 121 · Touristenattraktion 111 · **Spielplatz 108** · Café 97 · Bergrestaurant 94 · Gruppenunterkunft 88 · Themenweg 88 · Herberge 81 · Hotelkette 78.

→ Fast die Hälfte des Index sind Zimmer und Besprechungsräume. `search` schliesst `Accommodation` (Zimmer) und Besprechungsräume **per Default aus** und nimmt sie nur auf explizite Anfrage (`types`) herein — sonst verdrängen 61 Doppelzimmer des Hotel Du Nord jede Sehenswürdigkeit.

### 5.3 Recall-Ground-Truth Zürich (1.4b, Restprobe f)

| Quelle | Einträge |
|---|---:|
| zuerich.com «Zürich erleben» (17.09.2026): Sehenswürdigkeiten 258 · Essen & Trinken 499 · Nachtleben 224 · Shopping 171 · Kultur 133 · Erholung 275 | **1'481** |
| API `datasource=zht-cms`: civicStructures 260 · foodEstablishments 602 · localbusinesses 481 · places 22 · lodgingbusinesses 231 · events 0 · tours 0 | **1'596** |

Delta **+115 (+8 %)** — erklärt: Die Site zeigt kuratierte Kategorien (Mehrfachzuordnung möglich), der CMS-Export enthält auch nicht in «Zürich erleben» gelistete Objekte (Campingplätze, Ferienhäuser) und die Region (Einsiedeln, Rapperswil, Baar). Qualitativ: «Landesmuseum Zürich», «Erweiterungsbau Landesmuseum», «Shop Landesmuseum» existieren als Seiten auf zuerich.com — die ersten API-Treffer spiegeln die Site. **Recall bestätigt.** Canary: `datasource=zht-cms` gesamt ≥ 1'200.


### 5.4 Verifikation der Filter-Formate (17.09., 17 Calls, `PROBE_VERIFY_discover-swiss.md`)

| Frage | Befund |
|---|---|
| Facetten-Namen | Alle acht OData-Namen kommen zurück (`leafType`, `containedInPlace/id`, `rating/difficulty`, `address/addressLocality`, `categoryTree`, `sourcePartner`, `season`, `priceRange`); die filterPropertyName-Schreibweisen (`containedInPlace`, `ratingDifficulty`) werden **still verworfen** — Hypothese bestätigt |
| OData `filters` auf Touren | String und Array funktionieren; `length le 10000` (Meter) 29 von 220, `elevation/ascent le 300` 20, `rating/difficulty le 2` 22, kombiniert mit `and` 18 |
| Radius | `geo.distance(geo, geography'POINT(lon lat)') le <km>` ist ein echter Radius-Filter: 17 Webcams ≤ 25 km um St. Gallen, 83 Hotels ≤ 5 km um Interlaken; mit `scoringReferencePoint` zusätzlich nach Distanz sortiert |
| Events | `scheduleStart/scheduleEnd` als `YYYY-MM-DD` funktioniert (7 Treffer), aber laut Filter-Doku sind `count` und Paging damit **unzuverlässig** (Filter greift nach der Suche); `nextOccurrence` teils `None`. OData `schedule/any(item: item/endDate ge …)` liefert korrekte Zahlen (18) → Server nutzt OData |
| Gebiets-Auflösung | Facette `containedInPlace/id` mit `searchText=Glarnerland` → `ds_glarnerland` (345), daneben OSM-IDs (`osm_51701` Schweiz); Filter `containedInPlace=[ds_glarnerland]` → 117 Touren |
| Body-Arrays | `ratingDifficulty=["1","2"]` 22, `season=["sep"]` 19 — gleichwertig zu OData |

## 6. Architektur-Entscheid (Schritt 2)

**ARCH A (Live-API-only), Search-zentriert, mit Listen-Fallback.**

Rationale (live verifiziert 17.09.2026):
- `/search` deckt Volltext, Typ, Ort, Distanz, Datum und Facetten in einem Endpoint ab; Listen-Endpoints dienen nur `/vertices/{id}` (Detail) und dem Fallback.
- Kein Dump vorhanden; `updatedSince` erlaubt inkrementelles Caching, ist aber für Phase 1 nicht nötig.
- Rate-Limit 60/min, 50'000/Monat → Cache 15 min für Search, 24 h für Detail; `403 Quota` als eigener `degraded`-Status, nie retrien.

**Risiko und Gegenmassnahme:** Die Search-Berechtigung widerspricht der Doku und kann ohne Ankündigung entzogen werden. Deshalb (a) schriftliche Bestätigung durch discover.swiss im ersten Gespräch, (b) Fallback-Pfad im Server: bei 401/403 auf `/search` → Listen-Endpoint des Typs mit `containedInPlace=<area-id>` (7'290 Gebiete via `/areas`) und clientseitigem Distanzfilter aus `geo`. Der Fallback ist bewusst schmal (kein Volltext) und meldet sich als `provenance: list_fallback`.

**Project:** ausschliesslich `dsod-content`. `dsod-hs` ist Teilmenge (Grindelwald-Hostels erscheinen in `dsod-content`).

Platform-Lifecycle: `stable` (Release `20260910.2`, monatliche Releases laut Release-Notes-Struktur).

## 7. Tool-Design (8 Tools, alle `readOnlyHint: true`, alle mit `lang`)

| # | Tool | Quelle | Frage des Touristen |
|---|---|---|---|
| 1 | `search` | POST `/search` | «Was gibt es in Zürich / rund um Interlaken?» — `query`, `types[]`, `near{lat,lon}`, `locality`, `match: all\|name`, `page`; Default schliesst Zimmer und Besprechungsräume aus; `select` = 46 Felder, Treffer tragen Öffnungszeiten, Adresse, Geo, Bild, Lizenz bereits mit |
| 2 | `get_details` | `/vertices/{id}` | Beschreibung (HTML → Text), Preise (`fees`), Zürich Card, Barrierefreiheit, Öffnungszeiten, Ausstattung, Links; **gekürzt** (3 Fotos, Ausstattung als Namen, ≤ 8 KB); ND-Objekte: Text wörtlich, nicht paraphrasieren |
| 3 | `find_accommodation` | Search `type=LodgingBusiness` | Sterne, Garni, Preisspanne, Ausstattung, barrierefrei (Pro Infirmis/OK:GO als `sourcePartner`), Distanz |
| 4 | `find_tours` | Search `type=Tour` | Schwierigkeit, Länge, Aufstieg, Saison, Region; SchweizMobil-Touren mit CC BY |
| 5 | `find_events` | Search `type=Event` + `scheduleStart/End` | ⚠️ dünne Abdeckung (21) als Scope in der Tool-Description; **Testobjekte filtern** (`Demo|Test`, Platzhalter-Adressen) und als `excluded_test_objects` zählen |
| 6 | `webcams_near` | Search `type=Webcam` + `near` | 73 Webcams Ostschweiz; `link` = Livebild, `contentUrl` = letzter Snapshot (so beschriftet) |
| 7 | `explore_area` | Search mit `facets` (OData-Namen: `leafType`, `containedInPlace/id`, `sourcePartner`, `season`, `priceRange`) | «Was für Angebote gibt es in Region X?» — Antwort-Keys gegen Anfrage prüfen, fehlende Facetten melden |
| 8 | `source_status` | `/status`, Zähler | Erreichbarkeit, Calls/min, Monatsquota-Rest, letzter Abruf, Search verfügbar ja/nein |

Nicht bauen: Buchung/Verfügbarkeit (Marketplace, Phase 3), Wetter (`meteoswiss-mcp`), Anreise (`swiss-transport-mcp`), Bilder-Thumbnails (Media Service gesperrt).

**Envelope:** `source`, `provenance` (`live_api` / `cached` / `list_fallback`), `retrieved_at`, `project`, `attribution[]` pro Treffer (`provider`, `license`, `copyrightNotice`), `excluded_by_license`, `hint` bei Leermenge, `disclaimer` bei Öffnungszeiten/Preisen.

**Leermengen-Regeln (3.6):**
- `search` leer → `hint`: «Begriff kürzen (Präfix), `types` weglassen, `near` statt `locality`; Abdeckung ausserhalb Zürich/Ostschweiz/Unterkünfte ist gering — vorher `explore_area` prüfen.»
- `find_events` leer → `hint`: «Bestand ist klein; Zeitraum weiten; regionale Veranstaltungskalender nennen, nicht raten.»

## 8. Anchor Demo Queries (angepasst an den tatsächlichen Scope)

🎯 **Stadt (Zürich-Pilot):** *«Ich habe einen Regentag in Zürich — welche Museen sind in Gehdistanz zum HB, und wo esse ich danach vegetarisch?»* — Tools 1 + 2 + 3; Zürich Tourismus als Quelle (CC BY-SA), Attribution sichtbar.

🎯 **Outdoor (Glarnerland):** *«Ich bin in Braunwald: Welche Wanderungen mit wenig Höhenmetern gibt es, wie sieht es gerade auf der Webcam aus, und ist etwas gesperrt?»* — Tools 4 + 6 (discover) + `trail_closures` + `cable_cars_near` (swiss-tourism-mcp) + Wetter (`meteoswiss-mcp`). Zeigt beide Server zusammen.

🎯 **Unterkunft (national):** *«Family-friendly hotel near Interlaken, three stars, accessible — and how do I get there from Zurich airport?»* — Tool 3 mit Distanz-Ranking + `swiss-transport-mcp`.

Ground-Truth-Werte für Canaries: `Landesmuseum` ≥ 20 · `Grindelwald` ≥ 15 · `Wanderung` ≥ 200 · Hotels CH-weit ≥ 2'000 · Touren ≥ 100 · Webcams ≥ 30.

## 9. Offene Punkte

- [x] 1.4b Recall-Ground-Truth Zürich: +8 %, erklärt (5.3). Offen, optional: Braunwald-Touren gegen glarnerland.ch
- [x] Search-`select`-Whitelist (46 Felder), `FacetRequest`-Struktur, `resultsPerPage` bis 1'000 (Restprobe b–d)
- [x] `/vertices/{id}` für sechs Typen (5.1)
- [x] Facetten-Namen live bestätigt (5.4); OData-Filter, Radius, Event-Datumsfilter und Gebiets-Auflösung verifiziert
- [ ] HTML-Stripping + Entity-Auflösung als Testfall (Landesmuseum-Beschreibung als Fixture) → Bau, P1
- [ ] **Search-Berechtigung schriftlich bestätigen lassen** (Gespräch 1 mit discover.swiss) — vorher kein Release
- [ ] Recall-Canaries als `@pytest.mark.live` → Bau, P4
- [x] Notion-Portfolio-Karte angelegt (17.09.); Cluster «Tourism & Leisure» in portfolio.json: Copy-ready in HOUSEKEEPING_P3.md, Commit offen

## 10. Fundstücke für CHANGELOG «Known findings»

1. **Die Doku verneint Search, die API bejaht sie.** Live-Probe vor Design — der Skill hätte hier ohne Probe ein Tool-Set ohne Suche gebaut.
2. **`demo-web` ist partnergebunden.** Das Doku-Beispiel liefert 400; Projects kommen aus `/projects`.
3. **Paging heisst `nextPageToken`, nicht `continuation`.** Ein Boolean (`hasNextPage`) als Token gesendet → 400. Feldnamen aus der Live-Antwort lesen.
4. **`top=1000` heisst nicht 1000.** Cosmos DB schneidet bei ~4 MB (460 Zimmer) — immer dem Token folgen.
5. **Open-Produkt ≠ offene Lizenz.** Guidle-Events kommen mit All-Rights-Reserved, Hotelgruppen ohne Lizenz. Whitelist auf root-`license`.
6. **`ds-containedInPlaceFilter` ist kein Filter.** Der Header steuert, welche `containedInPlace`-Einträge in der Antwort erscheinen; der Treffer-Filter ist der Query-Parameter. *«Ein Header, der ‹Filter› heisst und die Antwort frisiert statt die Treffer — wie ein Türsteher, der nur die Garderobe sortiert.»*
7. **Schweiz Tourismus ist bereits Datenlieferant** (`sourcePartner` auf 2'769 Hotels, Datasource `st-sc`). Das ist ein Gesprächsargument: ihre Daten fliessen schon in den offenen Kanal.
8. **Facetten-Namen werden still ignoriert.** `containedInPlace` und `ratingDifficulty` als `name` → keine Fehlermeldung, keine Facette. Antwort-Keys immer gegen die Anfrage prüfen (I14Y-Lektion, zweiter Fall im Portfolio).
9. **Ein Hotel wiegt 78 KB.** 40 Fotos, 81 Ausstattungsmerkmale, Data-Governance-Ketten für jede Herkunft. Das Detail-Tool ist ein Filter, kein Durchreicher. *«Ein Tool, das ungekürzt weiterreicht, ist wie ein Reiseführer, der den ganzen Katalog vorliest.»*
10. **Testdaten im Produktivindex.** «Demo Event» mit «Strasse 1, PLZ Ort» liegt neben echten Events. Ein Tool, das nicht filtert, empfiehlt einem Touristen den Platzhalter.
11. **Beschreibungen sind HTML mit Entities.** `&uuml;` statt ü, `<p>`-Tags, Preise als `<table>`. Serverseitig auflösen, sonst halluziniert das Modell die Kodierung weg.
12. **Der Index ist zur Hälfte Zimmer und Besprechungsräume** (9'838 von 20'817). Ohne Typ-Default findet ein Tourist zuerst 61 Doppelzimmer.
13. **`geo.distance` ist ein echter Radius-Filter**, nicht nur ein Ranking — steht in der Filter-Doku, nicht in der Spec. Wer nur die OpenAPI liest, schneidet clientseitig.
14. **Der bequeme Event-Filter lügt beim Zählen.** `scheduleStart/End` greift nach der Suche; `count` und Paging stimmen nicht mehr, sagt die Doku selbst. Der OData-Weg ist umständlicher und korrekt. *«Der Filter, der auf der Packung steht, ist nicht der, der zählt.»*
15. **`nextOccurrence` kennt einen Sentinel: 2099-12-31.** Ein Event ohne konkreten Termin trägt das Jahr 2099 statt `null`. Ungeprüft weitergereicht empfiehlt der Assistent einen Anlass «am 31. Dezember 2099».
