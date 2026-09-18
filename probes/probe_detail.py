#!/usr/bin/env python3
"""
probe_detail.py — Restprobe discover.swiss (Punkt 2 der nächsten Schritte), ~25 Calls.

(a) /vertices/{id} vollständig für sechs Objekttypen → welche Felder liefert das Detail-Tool?
(b) /search: select-Whitelist verifizieren (alle 48 IndexResponse-Felder auf einmal, dann einzeln bei 400)
(c) /search: resultsPerPage-Maximum (10 / 50 / 100 / 200 / 500 / 1000)
(d) /search: FacetRequest als Objekte (leafType, containedInPlace, sourcePartner, ratingDifficulty)
(e) /search: searchFields=name vs. alle Felder → Recall-Delta für «Landesmuseum»

PowerShell:
    $env:DISCOVER_SWISS_KEY = "..."
    $env:PYTHONUTF8 = "1"
    python probe_detail.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.discover.swiss/info/v2"
PROJECT = "dsod-content"
KEY = os.environ.get("DISCOVER_SWISS_KEY") or sys.exit("DISCOVER_SWISS_KEY fehlt")
OUT = "probe_detail_out"
os.makedirs(OUT, exist_ok=True)

SAMPLE_IDS = {
    "civic_landesmuseum": "civ_px9-s28_bggg",
    "hotel_interlaken": "log_x8-tdgf_bcfch",
    "tour": "tou_s9t_acfeirar-ficg-ejes-qatg-crjfhetqhvev",
    "event": "eve_s9t_dshjrcer-tfsb-essd-rirq-hugidebuvjge",
    "webcam": "web_s9t_shavstqa-aetu-ehja-reuf-irehfjttijud",
    "restaurant": "foo_4kq_diaccjec",
}
# Alle Felder aus definitions.IndexResponse (Spec 20260910.2)
INDEX_FIELDS = [
    "@id", "ouaId", "identifier", "datasource", "dataGovernance", "type", "additionalType", "additionalProperty",
    "address", "geo", "geoDestination", "openingHours", "image", "name", "disambiguatingDescription", "description",
    "containedInPlace", "state", "time", "length", "rating", "tag", "campaignTag", "profileTag", "schedule",
    "openingHoursSpecification", "specialOpeningHoursSpecification", "nextOccurrence", "recurredCount", "elevation",
    "link", "autoTranslatedData", "ticketingContact", "priceInformation", "standardPrice", "potentialAction",
    "organizer", "lastModified", "sourceId", "hasReview", "location", "category", "productAvailability",
    "starRating", "context", "award", "relevanceScore", "awardSimplex",
]
LAST = [0.0]


def call(path, *, params=None, body=None, headers=None):
    time.sleep(max(0, 1.1 - (time.time() - LAST[0])))   # < 60/min
    LAST[0] = time.time()
    url = f"{BASE}{path}" + (("?" + urllib.parse.urlencode(params)) if params else "")
    h = {"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json", "Accept-Language": "de",
         "User-Agent": "swiss-public-data-mcp probe"}
    if headers:
        h.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    if data:
        h["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h,
                                                           method="POST" if data else "GET"), timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:  # noqa: BLE001
            return e.code, raw.decode(errors="replace")[:300]


def walk(o, prefix="", depth=0, out=None):
    """Feldpfade mit Typ und Grösse — für die Feldinventur des Detail-Objekts."""
    out = out if out is not None else []
    if isinstance(o, dict):
        for k, v in o.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)) and depth < 2:
                out.append((p, type(v).__name__, len(v)))
                walk(v, p, depth + 1, out)
            else:
                out.append((p, type(v).__name__, len(str(v))))
    elif isinstance(o, list) and o and depth < 2:
        walk(o[0], prefix + "[0]", depth + 1, out)
    return out


report = ["# PROBE_DETAIL — discover.swiss Restprobe\n", f"Datum: {time.strftime('%Y-%m-%d')} · Project `{PROJECT}`\n"]

# ---------------------------------------------------------------- (a) Detail-Objekte
print("▶ (a) /vertices/{id}")
report.append("## (a) Detail-Objekte via /vertices/{id}\n")
for label, oid in SAMPLE_IDS.items():
    st, obj = call(f"/vertices/{oid}", params={"project": PROJECT})
    size = len(json.dumps(obj, ensure_ascii=False))
    if st == 200 and isinstance(obj, dict):
        json.dump(obj, open(f"{OUT}/detail_{label}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        keys = sorted(obj.keys())
        desc = obj.get("description") or obj.get("disambiguatingDescription") or ""
        imgs = obj.get("image") or []
        img_url = (imgs[0].get("contentUrl") if isinstance(imgs, list) and imgs and isinstance(imgs[0], dict) else
                   imgs.get("contentUrl") if isinstance(imgs, dict) else None)
        ohs = obj.get("openingHoursSpecification")
        links = obj.get("url") or obj.get("link") or obj.get("sameAs")
        print(f"   {label:20s} HTTP {st}  {size:6d} B  {len(keys):2d} Felder  desc={len(desc):4d} Zeichen  "
              f"openingHours={'ja' if ohs else '-'}  image={'ja' if img_url else '-'}  link={'ja' if links else '-'}  "
              f"lic={obj.get('license')}")
        report.append(f"### {label} (`{oid}`) — HTTP {st}, {size} B, {len(keys)} Top-Level-Felder\n")
        report.append(f"- Lizenz: `{obj.get('license')}` · Copyright: {obj.get('copyrightNotice')} · "
                      f"description: {len(desc)} Zeichen · openingHoursSpecification: {'ja' if ohs else 'nein'} · "
                      f"image.contentUrl: {'ja' if img_url else 'nein'} · url/link: {'ja' if links else 'nein'} · "
                      f"removed: {obj.get('removed')}")
        report.append("- Felder: " + ", ".join(f"`{k}`" for k in keys) + "\n")
    else:
        print(f"   {label:20s} HTTP {st}  {str(obj)[:100]}")
        report.append(f"### {label} — HTTP {st}: {str(obj)[:200]}\n")

# ---------------------------------------------------------------- (b) select-Whitelist
print("▶ (b) /search select-Whitelist")
report.append("## (b) Search `select` — welche IndexResponse-Felder sind erlaubt?\n")
body = {"project": [PROJECT], "searchText": "Landesmuseum", "resultsPerPage": 2, "select": ",".join(INDEX_FIELDS)}
st, res = call("/search", body=body)
if st == 200:
    print("   alle 48 Felder auf einmal: 200 ✅")
    report.append("Alle 48 Felder in einem `select`: **200** — Whitelist = IndexResponse komplett.\n")
    json.dump(res, open(f"{OUT}/search_full_select.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    got = sorted(res["values"][0].keys()) if res.get("values") else []
    report.append("Tatsächlich gelieferte Felder im ersten Treffer: " + ", ".join(f"`{k}`" for k in got) + "\n")
else:
    print(f"   alle Felder: HTTP {st} → einzeln prüfen")
    bad, good = [], []
    for f in INDEX_FIELDS:
        st1, r1 = call("/search", body={**body, "select": f"identifier,{f}"})
        (good if st1 == 200 else bad).append(f)
        print(f"     {f:32s} {st1}")
    report.append("| erlaubt | abgelehnt (400) |\n|---|---|\n| " + ", ".join(f"`{x}`" for x in good) + " | "
                  + ", ".join(f"`{x}`" for x in bad) + " |\n")

# ---------------------------------------------------------------- (c) resultsPerPage
print("▶ (c) resultsPerPage-Maximum")
report.append("## (c) `resultsPerPage`\n\n| angefragt | HTTP | geliefert | count |\n|---|---|---|---|")
for n in (10, 50, 100, 200, 500, 1000):
    st, res = call("/search", body={"project": [PROJECT], "type": ["LodgingBusiness"], "resultsPerPage": n,
                                    "select": "identifier"})
    got = len(res.get("values", [])) if isinstance(res, dict) else 0
    print(f"   resultsPerPage={n:5d} → HTTP {st}  geliefert={got}  count={res.get('count') if isinstance(res, dict) else '-'}")
    report.append(f"| {n} | {st} | {got} | {res.get('count') if isinstance(res, dict) else str(res)[:80]} |")
report.append("")

# ---------------------------------------------------------------- (d) Facets als Objekte
print("▶ (d) FacetRequest-Objekte")
report.append("## (d) Facetten als `FacetRequest`-Objekte\n")
facets = [{"name": "leafType", "count": 25}, {"name": "containedInPlace", "count": 15},
          {"name": "sourcePartner", "count": 15}, {"name": "ratingDifficulty", "count": 5},
          {"name": "season", "count": 12}, {"name": "priceRange", "count": 5}]
st, res = call("/search", body={"project": [PROJECT], "resultsPerPage": 1, "select": "identifier", "facets": facets})
print(f"   HTTP {st}")
if st == 200:
    json.dump(res, open(f"{OUT}/search_facets.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    report.append(f"HTTP 200 · Gesamtbestand im Index (project={PROJECT}): **{res.get('count')}**\n")
    for fk, fv in (res.get("facets") or {}).items():
        vals = fv.get("values", []) if isinstance(fv, dict) else fv
        line = ", ".join(f"{v.get('name') or v.get('value')} ({v.get('count')})" for v in vals[:25])
        print(f"   {fk}: {line[:150]}")
        report.append(f"- **{fk}**: {line}")
    report.append("")
else:
    report.append(f"HTTP {st}: {str(res)[:300]}\n")

# ---------------------------------------------------------------- (e) searchFields
print("▶ (e) searchFields")
report.append("## (e) `searchFields` — worauf matcht der Volltext?\n\n| Begriff | Felder | count |\n|---|---|---|")
for term in ("Landesmuseum", "Grindelwald", "vegetarisch", "Rigi"):
    for sf in (None, "name", "name,disambiguatingDescription"):
        b = {"project": [PROJECT], "searchText": term, "resultsPerPage": 1, "select": "identifier"}
        if sf:
            b["searchFields"] = sf
        st, res = call("/search", body=b)
        c = res.get("count") if isinstance(res, dict) else f"HTTP {st}"
        print(f"   {term:14s} searchFields={str(sf):32s} count={c}")
        report.append(f"| {term} | {sf or '(alle)'} | {c} |")
report.append("")

# ---------------------------------------------------------------- (f) Recall-Ground-Truth Zürich (1.4b)
print("▶ (f) Ground Truth zuerich.com vs. API (datasource=zht-cms)")
SITE = {"gesamt «Zürich erleben»": 1481, "Sehenswürdigkeiten": 258, "Essen & Trinken": 499, "Nachtleben": 224,
        "Shopping": 171, "Kultur": 133, "Erholung": 275}   # zuerich.com/de/zuerich-erleben, abgerufen 17.09.2026
report.append("## (f) Recall-Ground-Truth Zürich (1.4b) — zuerich.com «Zürich erleben», 17.09.2026\n")
report.append("| zuerich.com | Einträge |\n|---|---|")
report += [f"| {k} | {v} |" for k, v in SITE.items()]
report.append("\n| API-Endpoint, `datasource=zht-cms` | Bestand | Typen (Seite 1, top 100) |\n|---|---|---|")
zht_total = 0
for ep in ("/civicStructures", "/foodEstablishments", "/localbusinesses", "/places", "/lodgingbusinesses", "/events",
           "/tours"):
    st, res = call(ep, params={"project": PROJECT, "datasource": "zht-cms", "top": 100, "includeCount": "true",
                               "select": "identifier,type,additionalType"})
    total = next((v for k, v in res.items() if isinstance(v, int) and "count" in k.lower()), None) if isinstance(res, dict) else None
    rows = res.get("data", []) if isinstance(res, dict) else []
    types = {}
    for o in rows:
        t = f"{o.get('additionalType') or o.get('type')}"
        types[t] = types.get(t, 0) + 1
    top = ", ".join(f"{k} {v}" for k, v in sorted(types.items(), key=lambda x: -x[1])[:6])
    zht_total += total or 0
    print(f"   {ep:22s} HTTP {st}  zht-cms total={total}  {top[:90]}")
    report.append(f"| `{ep}` | {total} | {top} |")
report.append(f"| **Summe** | **{zht_total}** | Site: 1'481 → Delta {zht_total - 1481:+d} |")
report.append("\nDelta-Hypothesen (zu prüfen): (1) Site listet nur publizierte/kuratierte Objekte, CMS-Export alles; "
              "(2) API umfasst Region (Winterthur, Rapperswil, Einsiedeln, Baar), Site nur Stadt — Facette "
              "`containedInPlace` in (d) zeigt die Verteilung; (3) Doppelrepräsentation (Landesmuseum als CivicStructure "
              "und als Place); (4) ArtObjects/Kunst im öffentlichen Raum sind auf der Site nicht gelistet.\n")
report.append("Qualitativ bestätigt (Web-Suche 17.09.): «Landesmuseum Zürich», «Erweiterungsbau Landesmuseum», "
              "«Shop Landesmuseum» existieren als eigene Seiten auf zuerich.com — die ersten vier API-Treffer "
              "spiegeln die Site.\n")

open("PROBE_DETAIL_discover-swiss.md", "w", encoding="utf-8").write("\n".join(report) + "\n")
print(f"\n✔ PROBE_DETAIL_discover-swiss.md + {OUT}/")
