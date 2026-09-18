# Housekeeping — Auszug für das Repo (Disclaimer-Texte, Lizenz-Entwurf)

Quelle: HOUSEKEEPING_P3.md vom 17.09.2026, Abschnitte 3 und 4a. Die übrigen Abschnitte (Portfolio-Einträge, Notion, Kalender) sind nicht Teil des Repos.

---

## 3. Disclaimer-Texte (Envelope-Feld `disclaimer`, kurz, viersprachig)

**A — Bedingungen und Sicherheit (`swiss-tourism-mcp`: Sperrungen, Lawinen, Herdenschutzhunde, Wildruhezonen, Badewasser)**

- DE: «Offizielle Daten von {Quelle}, Stand {Datum}. Keine Sicherheitsgarantie — Beschilderung, lokale Auskunft und das aktuelle Lawinenbulletin vor Ort sind massgebend.»
- FR: «Données officielles de {source}, état au {date}. Aucune garantie de sécurité — la signalisation, les renseignements locaux et le bulletin d'avalanches en vigueur font foi.»
- IT: «Dati ufficiali di {fonte}, stato al {data}. Nessuna garanzia di sicurezza — fanno stato la segnaletica, le informazioni locali e il bollettino valanghe in vigore.»
- EN: «Official data from {source}, as of {date}. No safety guarantee — on-site signage, local information and the current avalanche bulletin take precedence.»

**B — Inhalte (`discover-swiss-mcp`: Öffnungszeiten, Preise, Verfügbarkeit)**

- DE: «Angaben von {Anbieter} via discover.swiss, Stand {Datum}. Öffnungszeiten und Preise ohne Gewähr — vor dem Besuch beim Anbieter prüfen.»
- FR: «Informations de {prestataire} via discover.swiss, état au {date}. Horaires et prix sans garantie — à vérifier auprès du prestataire avant la visite.»
- IT: «Informazioni di {fornitore} via discover.swiss, stato al {data}. Orari e prezzi senza garanzia — verificare presso il fornitore prima della visita.»
- EN: «Information from {provider} via discover.swiss, as of {date}. Opening hours and prices without guarantee — check with the provider before visiting.»

Regel: Disclaimer A ist bei den Tools `trail_closures`, `avalanche_bulletin`, `guardian_dogs_near`, `access_rules_at`, `swimming_spots` immer gesetzt; B bei `get_details`, `find_accommodation`, `find_events`. Kein Tool leitet je «sicher» oder «offen» als Schlussfolgerung ab.

---

## 4. `docs/LICENSES.md` — Entwürfe

### 4a. `discover-swiss-mcp/docs/LICENSES.md`

```markdown
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
```
