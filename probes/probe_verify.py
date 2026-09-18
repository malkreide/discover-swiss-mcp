#!/usr/bin/env python3
"""
probe_verify.py — die letzten offenen Verifikationen vor dem Bau (≈ 14 Calls, < 1 Minute).

(1) Facetten mit OData-Namen: kommen containedInPlace/id, rating/difficulty, address/addressLocality, categoryTree zurück?
(2) OData `filters`: String vs. Array; length / elevation/ascent / rating/difficulty auf Touren
(3) geo.distance-Filter (Radius in km) — Webcams um St. Gallen, Hotels um Interlaken
(4) Events: scheduleStart/scheduleEnd als Datum (YYYY-MM-DD) und OData schedule/any(...)
(5) Gebiets-Auflösung: searchText «Glarnerland» → Facette containedInPlace/id → ID → Filter containedInPlace
(6) Body-Filter ratingDifficulty / season auf Touren

PowerShell:
    $env:DISCOVER_SWISS_KEY = "..."
    $env:PYTHONUTF8 = "1"
    python probe_verify.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://api.discover.swiss/info/v2"
PROJECT = "dsod-content"
KEY = os.environ.get("DISCOVER_SWISS_KEY") or sys.exit("DISCOVER_SWISS_KEY fehlt")
OUT = "probe_verify_out"
os.makedirs(OUT, exist_ok=True)
LAST = [0.0]
REPORT = ["# PROBE_VERIFY — discover.swiss, letzte Verifikationen\n", f"Datum: {dt.date.today().isoformat()} · Project `{PROJECT}`\n"]


def post(body: dict, label: str):
    time.sleep(max(0, 1.1 - (time.time() - LAST[0])))
    LAST[0] = time.time()
    h = {"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json", "Accept-Language": "de",
         "Content-Type": "application/json", "User-Agent": "swiss-public-data-mcp probe"}
    body = {"project": [PROJECT], **body}
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{BASE}/search", data=json.dumps(body).encode(),
                                                           headers=h, method="POST"), timeout=30) as r:
            st, res = r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            st, res = e.code, json.loads(raw)
        except Exception:  # noqa: BLE001
            st, res = e.code, raw.decode(errors="replace")[:300]
    json.dump({"request": body, "status": st, "response": res}, open(f"{OUT}/{label}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return st, res


def row(label, st, res, extra=""):
    if st == 200 and isinstance(res, dict):
        names = [str(v.get("name"))[:30] for v in res.get("values", [])[:3]]
        line = f"| {label} | {st} | count={res.get('count')} | {names} {extra} |"
    else:
        line = f"| {label} | {st} | {str(res)[:140].replace(chr(10), ' ')} | {extra} |"
    print("  " + line)
    REPORT.append(line)


# ---------------------------------------------------------------- (1) Facetten OData-Namen
print("▶ (1) Facetten mit OData-Namen")
REPORT.append("## (1) Facetten — OData-Namen\n\n| angefragt | HTTP | zurück | fehlend |\n|---|---|---|---|")
wanted = ["leafType", "containedInPlace/id", "rating/difficulty", "address/addressLocality", "categoryTree",
          "sourcePartner", "season", "priceRange"]
st, res = post({"resultsPerPage": 1, "select": "identifier", "facets": [{"name": n, "count": 10} for n in wanted]}, "f1_odata")
got = list((res.get("facets") or {}).keys()) if isinstance(res, dict) else []
missing = [n for n in wanted if n not in got]
print(f"  HTTP {st}  zurück={got}  fehlend={missing}")
REPORT.append(f"| {', '.join(wanted)} | {st} | {', '.join(got)} | {', '.join(missing) or '—'} |")
# Gegenprobe: filterPropertyName-Schreibweise
st2, res2 = post({"resultsPerPage": 1, "select": "identifier",
                  "facets": [{"name": "containedInPlace", "count": 5}, {"name": "ratingDifficulty", "count": 5}]}, "f1_filterprop")
got2 = list((res2.get("facets") or {}).keys()) if isinstance(res2, dict) else []
print(f"  Gegenprobe filterPropertyName: HTTP {st2}  zurück={got2}")
REPORT.append(f"| containedInPlace, ratingDifficulty (filterPropertyName) | {st2} | {', '.join(got2) or '—'} | {'beide' if not got2 else ''} |")

# ---------------------------------------------------------------- (2) OData filters auf Touren
print("▶ (2) OData filters (Touren)")
REPORT.append("\n## (2) OData `filters` auf `type=Tour`\n\n| Test | HTTP | Ergebnis | |\n|---|---|---|---|")
sel = "identifier,name,length,elevation,rating"
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel}, "f2_baseline"); row("Baseline Tour, kein Filter", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel, "filters": "length le 10000"}, "f2_len_str"); row("filters als String: length le 10000", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel, "filters": ["length le 10000"]}, "f2_len_arr"); row("filters als Array: [length le 10000]", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel, "filters": ["elevation/ascent le 300"]}, "f2_asc"); row("filters: elevation/ascent le 300", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel, "filters": ["rating/difficulty le 2"]}, "f2_diff"); row("filters: rating/difficulty le 2", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": sel, "filters": ["length le 10000 and elevation/ascent le 300"]}, "f2_combo"); row("filters: length le 10000 and elevation/ascent le 300", st, res)

# ---------------------------------------------------------------- (3) geo.distance
print("▶ (3) geo.distance-Radius")
REPORT.append("\n## (3) `geo.distance` (Radius in km)\n\n| Test | HTTP | Ergebnis | |\n|---|---|---|---|")
sg = "geo.distance(geo, geography'POINT(9.3767 47.4245)') le 25"
st, res = post({"type": ["Webcam"], "resultsPerPage": 3, "select": "identifier,name,geo", "filters": [sg]}, "f3_webcam_sg"); row("Webcams ≤ 25 km um St. Gallen", st, res)
il = "geo.distance(geo, geography'POINT(7.8632 46.6863)') le 5"
st, res = post({"type": ["LodgingBusiness"], "resultsPerPage": 3, "select": "identifier,name,address", "filters": [il]}, "f3_hotel_il"); row("Hotels ≤ 5 km um Interlaken", st, res)
st, res = post({"type": ["LodgingBusiness"], "resultsPerPage": 3, "select": "identifier,name,address", "filters": [il],
                "scoringReferencePoint": "7.8632,46.6863"}, "f3_hotel_il_scored"); row("dito + scoringReferencePoint (Radius + Distanz-Ranking)", st, res)

# ---------------------------------------------------------------- (4) Events
print("▶ (4) Events")
REPORT.append("\n## (4) Events — Datumsfilter\n\n| Test | HTTP | Ergebnis | |\n|---|---|---|---|")
today = dt.date.today(); end = today + dt.timedelta(days=90)
st, res = post({"type": ["Event"], "resultsPerPage": 5, "select": "identifier,name,nextOccurrence"}, "f4_all"); row("alle Events", st, res)
st, res = post({"type": ["Event"], "resultsPerPage": 5, "select": "identifier,name,nextOccurrence",
                "scheduleStart": today.isoformat(), "scheduleEnd": end.isoformat()}, "f4_sched")
nx = [v.get("nextOccurrence") for v in (res.get("values") or [])[:3]] if isinstance(res, dict) else []
row(f"scheduleStart={today} scheduleEnd={end} (Datum, CH-Zeit)", st, res, f"nextOccurrence={nx}")
st, res = post({"type": ["Event"], "resultsPerPage": 5, "select": "identifier,name,nextOccurrence",
                "filters": [f"schedule/any(item: item/endDate ge {today.isoformat()}T00:00:00Z)"]}, "f4_odata"); row("OData schedule/any(endDate ge heute)", st, res)

# ---------------------------------------------------------------- (5) Gebiets-Auflösung
print("▶ (5) Gebiets-Auflösung Glarnerland")
REPORT.append("\n## (5) Gebiet auflösen über Facette `containedInPlace/id`\n\n| Test | HTTP | Ergebnis | |\n|---|---|---|---|")
st, res = post({"searchText": "Glarnerland", "resultsPerPage": 1, "select": "identifier",
                "facets": [{"name": "containedInPlace/id", "count": 30}]}, "f5_facet")
area_id = None
if st == 200 and isinstance(res, dict):
    vals = (res.get("facets", {}).get("containedInPlace/id") or {}).get("values", [])
    hit = next((v for v in vals if str(v.get("name", "")).lower() == "glarnerland"), None)
    area_id = hit.get("value") if hit else None
    top = ", ".join(f"{v.get('name')}={v.get('value')} ({v.get('count')})" for v in vals[:6])
    print(f"  HTTP {st}  Glarnerland-ID={area_id}  Top: {top[:160]}")
    REPORT.append(f"| searchText=Glarnerland, Facette containedInPlace/id | {st} | Glarnerland → `{area_id}`; Top: {top[:200]} | |")
else:
    row("Facette containedInPlace/id", st, res)
if area_id:
    st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": "identifier,name", "containedInPlace": [area_id]}, "f5_filter")
    row(f"Touren mit containedInPlace=[{area_id}]", st, res)

# ---------------------------------------------------------------- (6) Body-Filter
print("▶ (6) Body-Filter ratingDifficulty / season")
REPORT.append("\n## (6) Body-Filter (Array-Parameter)\n\n| Test | HTTP | Ergebnis | |\n|---|---|---|---|")
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": "identifier,name,rating", "ratingDifficulty": ["1", "2"]}, "f6_diff"); row("ratingDifficulty=[1,2]", st, res)
st, res = post({"type": ["Tour"], "resultsPerPage": 3, "select": "identifier,name", "season": ["sep"]}, "f6_season"); row("season=[sep]", st, res)

REPORT.append("\n## Konsequenzen für die Prompts P2/P3\n\n- (1) → `explore_area`: gültige Facetten-Namen sind die, die in (1) zurückkamen; Tool-Description entsprechend.\n"
              "- (2) → `find_tours`: `filters` in der Form, die 200 lieferte (String oder Array); Felder `length` (Meter), `elevation/ascent`, `rating/difficulty`.\n"
              "- (3) → `webcams_near`, `search(near, radius_km)`: `geo.distance(geo, geography'POINT(lon lat)') le <km>` als echter Radius-Filter, kombiniert mit `scoringReferencePoint` fürs Ranking.\n"
              "- (4) → `find_events`: `scheduleStart`/`scheduleEnd` als `YYYY-MM-DD`; laut Doku ist `count` mit diesem Filter NICHT verlässlich und Paging nur als «nächste Seite» — im Envelope `upstream_count` als `None` und Hinweis setzen.\n"
              "- (5) → `resolve_area`: funktioniert über die Facette; ID-Format siehe oben.\n")
open("PROBE_VERIFY_discover-swiss.md", "w", encoding="utf-8").write("\n".join(REPORT) + "\n")
print(f"\n✔ PROBE_VERIFY_discover-swiss.md + {OUT}/")
