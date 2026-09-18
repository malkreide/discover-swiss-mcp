# PROBE_VERIFY — discover.swiss, letzte Verifikationen

Datum: 2026-09-17 · Project `dsod-content`

## (1) Facetten — OData-Namen

| angefragt | HTTP | zurück | fehlend |
|---|---|---|---|
| leafType, containedInPlace/id, rating/difficulty, address/addressLocality, categoryTree, sourcePartner, season, priceRange | 200 | leafType, containedInPlace/id, rating/difficulty, address/addressLocality, categoryTree, sourcePartner, season, priceRange | — |
| containedInPlace, ratingDifficulty (filterPropertyName) | 200 | — | beide |

## (2) OData `filters` auf `type=Tour`

| Test | HTTP | Ergebnis | |
|---|---|---|---|
| Baseline Tour, kein Filter | 200 | count=220 | ['Langlauf (Ski nordisch) im Thu', 'Velo-Rallye Bodensee', 'Krimi-Trail Frauenfeld']  |
| filters als String: length le 10000 | 200 | count=29 | ['Glarner Planetenweg', 'Glarner Wasserweg', 'Schlittelweg Kerenzerberg']  |
| filters als Array: [length le 10000] | 200 | count=29 | ['Glarner Planetenweg', 'Glarner Wasserweg', 'Schlittelweg Kerenzerberg']  |
| filters: elevation/ascent le 300 | 200 | count=20 | ['Glarner Planetenweg', 'Glarner Wasserweg', 'Zwerg Bartli-Erlebnisweg']  |
| filters: rating/difficulty le 2 | 200 | count=22 | ['Glarner Wasserweg', 'Schlittelweg Kerenzerberg', 'Zwerg Bartli-Erlebnisweg']  |
| filters: length le 10000 and elevation/ascent le 300 | 200 | count=18 | ['Glarner Planetenweg', 'Glarner Wasserweg', 'Zwerg Bartli-Erlebnisweg']  |

## (3) `geo.distance` (Radius in km)

| Test | HTTP | Ergebnis | |
|---|---|---|---|
| Webcams ≤ 25 km um St. Gallen | 200 | count=17 | ['Webcam St.Gallen, Kapfwaldweg', 'Webcam Säntis – der Berg', 'Webcam Thal, Rheinspitz']  |
| Hotels ≤ 5 km um Interlaken | 200 | count=83 | ['Hotel Chalet Swiss', 'Hotel Alpenblick', 'BnB Chalet-Gafri']  |
| dito + scoringReferencePoint (Radius + Distanz-Ranking) | 200 | count=83 | ['Hotel Du Nord', 'Backpackers Villa Sonnenhof', 'Hotel Jnterlaken']  |

## (4) Events — Datumsfilter

| Test | HTTP | Ergebnis | |
|---|---|---|---|
| alle Events | 200 | count=21 | ['JETZT - Kongress', 'Schweizer Genusswoche', 'Universität St.Gallen Promotio']  |
| scheduleStart=2026-09-17 scheduleEnd=2026-12-16 (Datum, CH-Zeit) | 200 | count=7 | ['Schweizer Genusswoche', 'Öffentliche Genuss-Degustation', 'Graduation Days'] nextOccurrence=[None, None, '2026-10-01T00:00:00+02:00'] |
| OData schedule/any(endDate ge heute) | 200 | count=18 | ['Schweizer Genusswoche', 'Universität St.Gallen Promotio', 'Demo Event']  |

## (5) Gebiet auflösen über Facette `containedInPlace/id`

| Test | HTTP | Ergebnis | |
|---|---|---|---|
| searchText=Glarnerland, Facette containedInPlace/id | 200 | Glarnerland → `ds_glarnerland`; Top: Schweiz=osm_51701 (351), Glarnerland=ds_glarnerland (345), Glarus=osm_1685673 (338), Glarner Alpen=osm_11342352 (327), Kinderregion=ds_kire (172), Glarus Süd=osm_1683141 (155) | |
| Touren mit containedInPlace=[ds_glarnerland] | 200 | count=117 | ['E-Bike Trophy Heidiland', 'Rundwanderung Mettmen-Leglerhü', 'Schneeschuhtour Id Schönau gu ']  |

## (6) Body-Filter (Array-Parameter)

| Test | HTTP | Ergebnis | |
|---|---|---|---|
| ratingDifficulty=[1,2] | 200 | count=22 | ['Glarner Wasserweg', 'Schlittelweg Kerenzerberg', 'Zwerg Bartli-Erlebnisweg']  |
| season=[sep] | 200 | count=19 | ['Glarner Planetenweg', 'Zwerg Bartli-Erlebnisweg', 'ELMER Citro Quellenweg']  |

## Konsequenzen für die Prompts P2/P3

- (1) → `explore_area`: gültige Facetten-Namen sind die, die in (1) zurückkamen; Tool-Description entsprechend.
- (2) → `find_tours`: `filters` in der Form, die 200 lieferte (String oder Array); Felder `length` (Meter), `elevation/ascent`, `rating/difficulty`.
- (3) → `webcams_near`, `search(near, radius_km)`: `geo.distance(geo, geography'POINT(lon lat)') le <km>` als echter Radius-Filter, kombiniert mit `scoringReferencePoint` fürs Ranking.
- (4) → `find_events`: `scheduleStart`/`scheduleEnd` als `YYYY-MM-DD`; laut Doku ist `count` mit diesem Filter NICHT verlässlich und Paging nur als «nächste Seite» — im Envelope `upstream_count` als `None` und Hinweis setzen.
- (5) → `resolve_area`: funktioniert über die Facette; ID-Format siehe oben.

