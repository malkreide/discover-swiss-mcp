# Data licences and attribution

The server forwards only objects whose root `license` is in the whitelist below. Everything else is counted in `excluded_by_license` and never served.

| Root licence | Served | Note |
|---|---|---|
| CC0, CC BY, CC BY-SA, ODbL | yes | attribution per object |
| CC BY-ND | yes | descriptions verbatim, never paraphrased (tool description enforces this) |
| CC BY-NC-*, C-All-Rights-Reserved, Unknown, null | no | counted only |

Attribution per hit is built from the object: `copyrightNotice` (e.g. «Zürich Tourismus www.zuerich.com»), `dataGovernance.provider.name`, `license`. Origins (`dataGovernance.origin[]`) are kept for provenance, not for display.

Platform terms: discover.swiss Infocenter Open, subscription key per user (bring-your-own-key). Rate limit 60 calls/min, 50'000/month. The docs ask partners to get in touch before productive use — see README «Status» for the state of that conversation.

Providers seen in the open index (17.09.2026): HotellerieSuisse, Schweiz Tourismus, VISIT Glarnerland, Thurgau Tourismus, St. Gallen-Bodensee Tourismus, Zürich Tourismus, Pro Infirmis, Heidiland, Appenzellerland Tourismus, Liechtenstein Marketing, GastroSuisse, Engadin Scuol, Toggenburg, OK:GO, SchweizMobil (CC BY), TOMAS (CC BY-ND).

---

## Disclaimer text (envelope field `disclaimer`)

Set on every tool that returns opening hours, prices or availability — in P1
that is `get_details`, `find_accommodation` and `find_events`. It is mandatory,
not optional: the probe found tour opening hours carried as free text still
naming the year 2024.

- DE: «Angaben von {Anbieter} via discover.swiss, Stand {Datum}. Öffnungszeiten und Preise ohne Gewähr — vor dem Besuch beim Anbieter prüfen.»
- FR: «Informations de {prestataire} via discover.swiss, état au {date}. Horaires et prix sans garantie — à vérifier auprès du prestataire avant la visite.»
- IT: «Informazioni di {fornitore} via discover.swiss, stato al {data}. Orari e prezzi senza garanzia — verificare presso il fornitore prima della visita.»
- EN: «Information from {provider} via discover.swiss, as of {date}. Opening hours and prices without guarantee — check with the provider before visiting.»

## Software licence

The software in this repository is MIT (see [LICENSE](../LICENSE)). The data is
not: it stays under the licence of the provider named in each hit.
