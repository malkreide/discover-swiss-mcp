# PROBE_DETAIL — discover.swiss Restprobe

Datum: 2026-09-17 · Project `dsod-content`

## (a) Detail-Objekte via /vertices/{id}

### civic_landesmuseum (`civ_px9-s28_bggg`) — HTTP 200, 38664 B, 41 Top-Level-Felder

- Lizenz: `CC BY-SA` · Copyright: Zürich Tourismus www.zuerich.com · description: 1634 Zeichen · openingHoursSpecification: ja · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `accessibility`, `additionalProperty`, `additionalType`, `address`, `autoTranslatedData`, `availableDataLanguage`, `award`, `campaignTag`, `category`, `containedInPlace`, `copyright`, `copyrightNotice`, `dataGovernance`, `description`, `detailedInformation`, `disambiguatingDescription`, `fees`, `geo`, `identifier`, `image`, `lastModified`, `license`, `link`, `located`, `name`, `openingDays`, `openingHoursSpecification`, `osm_id`, `photo`, `potentialAction`, `removed`, `specialOpeningHoursSpecification`, `tag`, `telephone`, `textTeaser`, `titleTeaser`, `type`, `url`, `zurichcard`, `zurichcardDescription`

### hotel_interlaken (`log_x8-tdgf_bcfch`) — HTTP 200, 77738 B, 34 Top-Level-Felder

- Lizenz: `CC BY` · Copyright: None · description: 841 Zeichen · openingHoursSpecification: nein · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `accessibility`, `additionalProperty`, `additionalType`, `address`, `amenityFeature`, `autoTranslatedData`, `availableDataLanguage`, `availableLanguage`, `category`, `checkinTime`, `checkinTimeTo`, `checkoutTime`, `checkoutTimeFrom`, `containedInPlace`, `dataGovernance`, `description`, `geo`, `identifier`, `image`, `lastModified`, `license`, `link`, `name`, `numberOfBeds`, `numberOfRooms`, `paymentAccepted`, `photo`, `removed`, `starRating`, `tag`, `telephone`, `type`, `url`

### tour (`tou_s9t_acfeirar-ficg-ejes-qatg-crjfhetqhvev`) — HTTP 200, 18631 B, 25 Top-Level-Felder

- Lizenz: `CC BY-SA` · Copyright: None · description: 653 Zeichen · openingHoursSpecification: nein · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `additionalType`, `address`, `autoTranslatedData`, `availableDataLanguage`, `category`, `containedInPlace`, `dataGovernance`, `description`, `disambiguatingDescription`, `geo`, `identifier`, `image`, `lastModified`, `license`, `link`, `name`, `openingHours`, `osm_id`, `photo`, `potentialAction`, `removed`, `telephone`, `type`, `url`

### event (`eve_s9t_dshjrcer-tfsb-essd-rirq-hugidebuvjge`) — HTTP 200, 16269 B, 26 Top-Level-Felder

- Lizenz: `CC BY-SA` · Copyright: None · description: 19 Zeichen · openingHoursSpecification: nein · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `autoTranslatedData`, `availableDataLanguage`, `category`, `containedInPlace`, `dataGovernance`, `description`, `disambiguatingDescription`, `endDate`, `eventSchedule`, `eventStatus`, `identifier`, `image`, `lastModified`, `license`, `link`, `location`, `name`, `nextOccurrence`, `organizer`, `photo`, `potentialAction`, `removed`, `startDate`, `type`, `url`

### webcam (`web_s9t_shavstqa-aetu-ehja-reuf-irehfjttijud`) — HTTP 200, 6225 B, 17 Top-Level-Felder

- Lizenz: `CC BY-SA` · Copyright: None · description: 0 Zeichen · openingHoursSpecification: nein · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `autoTranslatedData`, `availableDataLanguage`, `containedInPlace`, `dataGovernance`, `geo`, `identifier`, `image`, `lastModified`, `license`, `link`, `name`, `osm_id`, `photo`, `potentialAction`, `removed`, `type`

### restaurant (`foo_4kq_diaccjec`) — HTTP 200, 32669 B, 27 Top-Level-Felder

- Lizenz: `CC BY-SA` · Copyright: None · description: 908 Zeichen · openingHoursSpecification: nein · image.contentUrl: ja · url/link: ja · removed: False
- Felder: `@id`, `additionalProperty`, `additionalType`, `address`, `amenityFeature`, `autoTranslatedData`, `availableDataLanguage`, `campaignTag`, `containedInPlace`, `dataGovernance`, `description`, `disambiguatingDescription`, `geo`, `identifier`, `image`, `lastModified`, `license`, `link`, `name`, `openingHours`, `osm_id`, `photo`, `removed`, `tag`, `telephone`, `type`, `url`

## (b) Search `select` — welche IndexResponse-Felder sind erlaubt?

| erlaubt | abgelehnt (400) |
|---|---|
| `@id`, `ouaId`, `identifier`, `datasource`, `dataGovernance`, `type`, `additionalType`, `additionalProperty`, `address`, `geo`, `geoDestination`, `openingHours`, `image`, `name`, `disambiguatingDescription`, `description`, `state`, `time`, `length`, `rating`, `tag`, `campaignTag`, `profileTag`, `schedule`, `openingHoursSpecification`, `specialOpeningHoursSpecification`, `nextOccurrence`, `recurredCount`, `elevation`, `link`, `autoTranslatedData`, `ticketingContact`, `priceInformation`, `standardPrice`, `potentialAction`, `organizer`, `lastModified`, `sourceId`, `hasReview`, `location`, `category`, `productAvailability`, `starRating`, `award`, `relevanceScore`, `awardSimplex` | `containedInPlace`, `context` |

## (c) `resultsPerPage`

| angefragt | HTTP | geliefert | count |
|---|---|---|---|
| 10 | 200 | 10 | 5275 |
| 50 | 200 | 50 | 5275 |
| 100 | 200 | 100 | 5275 |
| 200 | 200 | 200 | 5275 |
| 500 | 200 | 500 | 5275 |
| 1000 | 200 | 1000 | 5275 |

## (d) Facetten als `FacetRequest`-Objekte

HTTP 200 · Gesamtbestand im Index (project=dsod-content): **20817**

- **leafType**: Hotelzimmer (5314), Besprechungsraum (4524), Hotel (3093), Beherbergungsbetrieb (1394), Restaurant (906), Freizeit/Dienstleistung (344), Ort (322), Ferienwohnung (276), Sportanlage (216), Geschäft (215), Museum (202), Feuerstelle (176), Bar (153), Angebot (152), Wohnung (141), Ferienhaus (121), Touristenattraktion (111), Spielplatz (108), Café (97), Bergrestaurant (94), Unterkunft (91), Gruppenunterkunft (88), Themenweg (88), Herberge (81), Hotelkette (78)
- **sourcePartner**: HotellerieSuisse (9619), Schweiz Tourismus (3072), VISIT Glarnerland AG (1752), Thurgau Tourismus (1381), St.Gallen-Bodensee Tourismus (1338), Zürich Tourismus (1311), Pro Infirmis (1049), Heidiland Tourismus AG (711), Appenzellerland Tourismus AR (608), Liechtenstein Marketing (553), GastroSuisse (453), Tourismus Engadin Scuol Samnaun Val Müstair AG (429), Toggenburg Tourismus (421), OK:GO Initiative - Förderverein Barrierefreie Schweiz (401)
- **season**: Januar (16), Februar (16), März (14), April (10), Mai (15), Juni (19), Juli (20), August (20), September (19), Oktober (18), November (7), Dezember (15)
- **priceRange**: Niedrig (292), Mittel (245), Hoch (46)

## (e) `searchFields` — worauf matcht der Volltext?

| Begriff | Felder | count |
|---|---|---|
| Landesmuseum | (alle) | 53 |
| Landesmuseum | name | 7 |
| Landesmuseum | name,disambiguatingDescription | 15 |
| Grindelwald | (alle) | 37 |
| Grindelwald | name | 7 |
| Grindelwald | name,disambiguatingDescription | 7 |
| vegetarisch | (alle) | 136 |
| vegetarisch | name | 0 |
| vegetarisch | name,disambiguatingDescription | 16 |
| Rigi | (alle) | 49 |
| Rigi | name | 25 |
| Rigi | name,disambiguatingDescription | 25 |

## (f) Recall-Ground-Truth Zürich (1.4b) — zuerich.com «Zürich erleben», 17.09.2026

| zuerich.com | Einträge |
|---|---|
| gesamt «Zürich erleben» | 1481 |
| Sehenswürdigkeiten | 258 |
| Essen & Trinken | 499 |
| Nachtleben | 224 |
| Shopping | 171 |
| Kultur | 133 |
| Erholung | 275 |

| API-Endpoint, `datasource=zht-cms` | Bestand | Typen (Seite 1, top 100) |
|---|---|---|
| `/civicStructures` | 260 | Museum 71, PerformingArtsTheater 15, ArtObject 6, TouristAttraction 2, ConcertHall 2, Church 1 |
| `/foodEstablishments` | 602 | Restaurant 80, CafeOrCoffeeShop 9, Winery 7, BarOrPub 4 |
| `/localbusinesses` | 481 | SportsActivityLocation 63, Store 25, NightClub 5, PublicSwimmingPool 3, DaySpa 2, EntertainmentBusiness 1 |
| `/places` | 22 | Landform 15, schema.org/Place 7 |
| `/lodgingbusinesses` | 231 | Hotel 87, Campground 6, HolidayHouse 4, BedAndBreakfast 2, HolidayApartment 1 |
| `/events` | 0 |  |
| `/tours` | 0 |  |
| **Summe** | **1596** | Site: 1'481 → Delta +115 |

Delta-Hypothesen (zu prüfen): (1) Site listet nur publizierte/kuratierte Objekte, CMS-Export alles; (2) API umfasst Region (Winterthur, Rapperswil, Einsiedeln, Baar), Site nur Stadt — Facette `containedInPlace` in (d) zeigt die Verteilung; (3) Doppelrepräsentation (Landesmuseum als CivicStructure und als Place); (4) ArtObjects/Kunst im öffentlichen Raum sind auf der Site nicht gelistet.

Qualitativ bestätigt (Web-Suche 17.09.): «Landesmuseum Zürich», «Erweiterungsbau Landesmuseum», «Shop Landesmuseum» existieren als eigene Seiten auf zuerich.com — die ersten vier API-Treffer spiegeln die Site.

