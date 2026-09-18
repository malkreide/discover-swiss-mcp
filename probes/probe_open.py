#!/usr/bin/env python3
"""
probe_open.py — die offenen Fragen aus STOP-GATE P1 (13 Calls, höchstens 31, < 1 Minute).

Nach dem Muster von probe_verify.py: nur Standardbibliothek, Rohantworten werden
gespeichert, der Report entsteht beim Lauf. Die Probe ist die Wahrheit, nicht die
Doku — deshalb misst dieses Skript vier Annahmen, auf denen P1-Code bereits steht
oder auf denen P2-Code stehen würde.

(1) Filtert der Query-Parameter `containedInPlace` auf den LISTEN-Endpoints wirklich
    die Treffer? Der Report schreibt den Fallback so vor, aber kein gespeichertes
    Artefakt belegt es, und die OpenAPI führt den Parameter bei /accommodations gar
    nicht auf. Gegenprobe gegen die Search-Seite, wo der Filter verifiziert ist:
    Stimmen beide Zahlen überein, filtert er. Zusätzlich eine Unsinns-ID — bleibt
    die Zahl unverändert, wird der Parameter still ignoriert (die I14Y-Lektion:
    ein Parameter, der nichts tut und nichts sagt, ist die teuerste Sorte).

(2) Welche Felder gehen im Listen-`select` durch? P1 sendet exakt die neun Felder,
    die die Erstprobe belegt hat. `address`, `url`, `link`, `image`, `lastModified`
    und `telephone` würden den Fallback brauchbar machen — aber jeder Listen-
    Endpoint hat eine eigene Response-Definition, ein Feld kann auf einem 200 und
    auf dem nächsten 400 liefern. Erst alle zusammen, bei 400 einzeln (Muster aus
    probe_detail.py (b)).

(3) Welches Feld trägt die Gesamtzahl bei `includeCount=true`? Die Spec sagt
    `count`; P1 liest tolerant. Kostet keinen eigenen Call — die Antwort-Keys aus
    (1) sagen es.

(4) Wie lautet der echte 429-Body? Der Client parst die Sekunden aus
    «Try again in N seconds»; die Formulierung ist aus dem Gateway-Standard
    abgeleitet, nicht gemessen. Nur mit --rate-limit, weil dieser Test bewusst ins
    Limit fährt und dafür ~60 Calls des Monatskontingents verbraucht.

Aufruf (aus probes/ heraus):
    export DISCOVER_SWISS_KEY="..."
    export PYTHONUTF8=1
    python probe_open.py                 # (1)–(3)
    python probe_open.py --rate-limit    # zusätzlich (4)

Budget: 13 Calls, wenn alle Zusatzfelder auf Anhieb durchgehen; höchstens 31, wenn jeder
der drei Endpoints die Kandidaten einzeln prüfen lässt. Mit --rate-limit kommen ~60 dazu.
Eigener Token-Bucket auf 55/min wie in probe_discover_swiss.py, Abbruch bei 403 Quota.

Alle fünf Befund-Zweige von (1) sind offline gegen einen gestubbten call() durchgespielt —
das Skript soll beim ersten Live-Lauf keine Calls an einem Absturz verbrennen.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.discover.swiss/info/v2"
PROJECT = "dsod-content"
# Bewusst nicht mit sys.exit() auf Modulebene wie in den Geschwister-Skripten:
# `--help` ist das Erste, was man bei einem neuen Flag aufruft, und soll auch ohne
# Key antworten. Der Abbruch steht in main().
KEY = os.environ.get("DISCOVER_SWISS_KEY", "")
OUT = "probe_open_out"
UA = "swiss-public-data-mcp probe (https://github.com/malkreide)"

# Die neun Felder, die P1 als LIST_SELECT sendet — belegt durch die Erstprobe.
BASE_SELECT = "identifier,name,type,additionalType,license,copyrightNotice,dataGovernance,geo,containedInPlace"
# Kandidaten für (2). Mehr wäre Neugier; das sind die, die der Fallback braucht.
CANDIDATE_FIELDS = ["address", "url", "link", "image", "lastModified", "telephone"]
SELECT_ENDPOINTS = ["/lodgingbusinesses", "/civicStructures", "/webcams"]

# Eine ID, die es nicht gibt. Bleibt der Bestand damit unverändert, wird der
# Parameter still verworfen.
NONSENSE_AREA = "ds_this_area_does_not_exist"

CALLS: list[dict] = []
RATE_WINDOW: list[float] = []
REPORT: list[str] = []


# ----------------------------------------------------------------------------- HTTP
def _throttle() -> None:
    """Eigener Bucket auf 55/min — dieselbe Bremse wie im Client."""
    now = time.time()
    RATE_WINDOW[:] = [t for t in RATE_WINDOW if now - t < 60]
    if len(RATE_WINDOW) >= 55:
        wait = 60 - (now - RATE_WINDOW[0]) + 0.5
        print(f"   … Rate-Limit-Schutz: warte {wait:.0f}s", file=sys.stderr)
        time.sleep(max(wait, 0))
    RATE_WINDOW.append(time.time())


def call(path, *, params=None, body=None, method="GET", label="", throttle=True):
    url = f"{BASE}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
    hdrs = {"Ocp-Apim-Subscription-Key": KEY, "User-Agent": UA, "Accept": "application/json",
            "Accept-Language": "de", "categoryVersion": "sui"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    if throttle:
        _throttle()
    t0 = time.time()
    status, raw, rh = 0, b"", {}
    try:
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            status, raw, rh = resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        status, raw, rh = e.code, e.read(), dict(e.headers)
    except Exception as e:  # noqa: BLE001
        status, raw = -1, str(e).encode()
    try:
        payload = json.loads(raw) if raw else {}
    except Exception:  # noqa: BLE001
        payload = raw.decode(errors="replace")[:500]
    CALLS.append({"label": label, "method": method, "url": url, "status": status,
                  "ms": round((time.time() - t0) * 1000), "bytes": len(raw)})
    if status == 403 and "quota" in json.dumps(payload, default=str).lower():
        print("\n!! HTTP 403 Quota Exceeded — Monatskontingent erschöpft. Abbruch.", file=sys.stderr)
        save("calls.json", CALLS)
        sys.exit(2)
    return status, payload, rh


def search(body: dict, label: str):
    return call("/search", body={"project": [PROJECT], **body}, method="POST", label=label)


def save(name: str, obj) -> None:
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def count_of(payload):
    """Gesamtzahl aus includeCount=true — tolerant, damit (3) die Frage beantwortet."""
    if not isinstance(payload, dict):
        return None, None
    if isinstance(payload.get("count"), int):
        return payload["count"], "count"
    for k, v in payload.items():
        if isinstance(v, int) and not isinstance(v, bool) and re.search(r"count|total", k, re.I):
            return v, k
    return None, None


def msg_of(payload) -> str:
    if isinstance(payload, dict):
        return str(payload.get("message") or payload.get("title") or payload)[:160]
    return str(payload)[:160]


def facet_values(payload, name):
    f = (payload.get("facets") or {}).get(name) if isinstance(payload, dict) else None
    return (f or {}).get("values", []) if isinstance(f, dict) else []


def resolve_area(name: str, label: str):
    """Gebiet über die Facette auflösen — derselbe Weg, den client.resolve_area geht."""
    st, res, _ = search({"searchText": name, "resultsPerPage": 1, "select": "identifier",
                         "facets": [{"name": "containedInPlace/id", "count": 30}]}, label)
    save(f"{label}.json", {"status": st, "response": res})
    vals = facet_values(res, "containedInPlace/id")
    hit = next((v for v in vals if str(v.get("name", "")).strip().lower() == name.strip().lower()), None)
    top = ", ".join(f"{v.get('name')}={v.get('value')} ({v.get('count')})" for v in vals[:4])
    return (hit.get("value") if hit else None), top


# ----------------------------------------------------------------------------- (1) + (3)
def probe_contained_in_place(count_field_seen: set) -> None:
    print("▶ (1) containedInPlace auf Listen-Endpoints — filtert der Parameter?")
    REPORT.append("## (1) `containedInPlace` als Query-Parameter auf Listen-Endpoints\n")
    REPORT.append("Gegenprobe ist die Search-Seite, wo der Filter verifiziert ist. "
                  "Stimmen Listen- und Search-Zahl überein, filtert der Parameter; bleibt die "
                  "Listenzahl auf dem Gesamtbestand, wird er still ignoriert.\n")
    REPORT.append("| Endpoint | Gebiet | Bestand gesamt | Liste gefiltert | Search gefiltert | Unsinns-ID | Befund |")
    REPORT.append("|---|---|---:|---:|---:|---:|---|")

    # Gebiet 1 ist live verifiziert (Glarnerland → ds_glarnerland, Restprobe f5);
    # Gebiet 2 wird zur Laufzeit aufgelöst, das prüft resolve_area gleich mit.
    cases = []
    for area_name, endpoint, search_type in (
        ("Glarnerland", "/tours", "Tour"),
        ("Zürich", "/civicStructures", "CivicStructure"),
    ):
        area_id, top = resolve_area(area_name, f"area_{area_name.lower().replace('ü', 'ue')}")
        print(f"   Gebiet «{area_name}» → {area_id or 'KEIN exakter Treffer'}   Top: {top[:110]}")
        REPORT.append(f"| _Auflösung_ | «{area_name}» → `{area_id}` | | | | | Facette: {top[:120]} |")
        if not area_id:
            continue
        cases.append((endpoint, area_name, area_id, search_type))

    for endpoint, area_name, area_id, search_type in cases:
        base_params = {"project": PROJECT, "top": 1, "includeCount": "true", "select": "identifier"}

        st_all, pl_all, _ = call(endpoint, params=base_params,
                                 label=f"all{endpoint}")
        total_all, field = count_of(pl_all)
        if field:
            count_field_seen.add(field)
        if isinstance(pl_all, dict):
            save(f"envelope{endpoint.replace('/', '_')}.json",
                 {"keys": sorted(pl_all.keys()), "count_field": field, "sample": pl_all})

        st_f, pl_f, _ = call(endpoint, params={**base_params, "containedInPlace": area_id},
                             label=f"filtered{endpoint}")
        total_filtered, _ = count_of(pl_f)

        st_n, pl_n, _ = call(endpoint, params={**base_params, "containedInPlace": NONSENSE_AREA},
                             label=f"nonsense{endpoint}")
        total_nonsense, _ = count_of(pl_n)

        st_s, pl_s, _ = search({"type": [search_type], "containedInPlace": [area_id],
                                "resultsPerPage": 1, "select": "identifier"}, f"search{endpoint.replace('/', '_')}")
        total_search = pl_s.get("count") if isinstance(pl_s, dict) else None

        verdict = _verdict(st_f, total_all, total_filtered, total_nonsense, total_search)
        print(f"   {endpoint:20s} {area_name:12s} gesamt={total_all} gefiltert={total_filtered} "
              f"search={total_search} unsinn={total_nonsense}  → {verdict}")
        REPORT.append(f"| `{endpoint}` | {area_name} (`{area_id}`) | {total_all} | "
                      f"{total_filtered if st_f == 200 else f'HTTP {st_f}'} | {total_search} | "
                      f"{total_nonsense} | {verdict} |")
    REPORT.append("")


def _verdict(status, total_all, filtered, nonsense, search_total) -> str:
    if status != 200:
        return "❌ Parameter abgelehnt — Fallback muss clientseitig über `geo` filtern"
    if filtered is None or total_all is None:
        return "⚠️ keine Zahl lesbar — Envelope prüfen"
    if filtered == total_all and nonsense == total_all:
        return "❌ **still ignoriert** — Parameter tut nichts, meldet nichts"
    if filtered < total_all and nonsense in (0, None):
        if search_total is not None and filtered == search_total:
            return "✅ filtert, Zahl deckt sich mit der Search-Seite"
        return f"✅ filtert, weicht aber von der Search-Zahl ab ({search_total}) — Typ-Zuschnitt prüfen"
    if filtered < total_all and nonsense == total_all:
        return "⚠️ filtert bei echter ID, ignoriert die Unsinns-ID — ein Tippfehler liefert stillschweigend alles"
    return "⚠️ uneindeutig — Rohantworten in probe_open_out/ ansehen"


# ----------------------------------------------------------------------------- (2)
def probe_select_fields() -> None:
    print("▶ (2) Listen-`select` — welche Zusatzfelder gehen durch?")
    REPORT.append("## (2) Zusatzfelder im Listen-`select`\n")
    REPORT.append(f"Basis (P1, belegt): `{BASE_SELECT}`\n")
    REPORT.append("| Endpoint | alle Kandidaten zusammen | erlaubt | abgelehnt |")
    REPORT.append("|---|---|---|---|")

    for endpoint in SELECT_ENDPOINTS:
        params = {"project": PROJECT, "top": 1,
                  "select": BASE_SELECT + "," + ",".join(CANDIDATE_FIELDS)}
        st, pl, _ = call(endpoint, params=params, label=f"select-all{endpoint}")
        if st == 200:
            print(f"   {endpoint:22s} alle {len(CANDIDATE_FIELDS)} zusammen: 200")
            REPORT.append(f"| `{endpoint}` | HTTP 200 | {', '.join(f'`{f}`' for f in CANDIDATE_FIELDS)} | — |")
            rows = pl.get("data") if isinstance(pl, dict) else None
            if rows:
                # Ein 200 heisst nicht, dass das Feld auch gefüllt ankommt.
                present = sorted(k for k in rows[0] if k in CANDIDATE_FIELDS)
                REPORT.append(f"| | _in der Antwort tatsächlich vorhanden_ | {', '.join(present) or '—'} | |")
                save(f"select_row{endpoint.replace('/', '_')}.json", rows[0])
            continue

        print(f"   {endpoint:22s} alle zusammen: HTTP {st} — {msg_of(pl)[:70]} → einzeln")
        ok, bad = [], []
        for field in CANDIDATE_FIELDS:
            st1, pl1, _ = call(endpoint, params={"project": PROJECT, "top": 1,
                                                 "select": BASE_SELECT + "," + field},
                               label=f"select-{field}{endpoint}")
            (ok if st1 == 200 else bad).append(field if st1 == 200 else f"{field} ({st1})")
            print(f"      {field:14s} {'200' if st1 == 200 else f'HTTP {st1}'}")
        REPORT.append(f"| `{endpoint}` | HTTP {st} | {', '.join(f'`{f}`' for f in ok) or '—'} | "
                      f"{', '.join(f'`{f}`' for f in bad) or '—'} |")
    REPORT.append("")


# ----------------------------------------------------------------------------- (3)
def report_count_field(count_field_seen: set) -> None:
    REPORT.append("## (3) Feldname der Gesamtzahl bei `includeCount=true`\n")
    if count_field_seen:
        names = ", ".join(f"`{n}`" for n in sorted(count_field_seen))
        REPORT.append(f"Gemessen: {names}. Envelope-Keys je Endpoint in `{OUT}/envelope_*.json`.\n")
        print(f"▶ (3) Zählfeld: {names}")
    else:
        REPORT.append("⚠️ Kein Zählfeld gefunden — `includeCount=true` liefert keine Zahl. "
                      "Der Client liest tolerant und meldet dann `total: None`.\n")
        print("▶ (3) Zählfeld: KEINES gefunden")


# ----------------------------------------------------------------------------- (4)
def probe_rate_limit() -> None:
    """Fährt bewusst ins Limit. Kostet ~60 Calls des Monatskontingents."""
    print("▶ (4) 429-Body — fährt bewusst ins Limit (~60 Calls)")
    REPORT.append("## (4) Der echte 429-Body\n")
    hit = None
    for i in range(80):
        st, pl, rh = call("/webcams", params={"project": PROJECT, "top": 1, "select": "identifier"},
                          label=f"burst-{i}", throttle=False)
        if st == 429:
            hit = {"attempt": i + 1, "body": pl, "headers": rh}
            break
    if not hit:
        REPORT.append("Kein 429 nach 80 Calls — das Limit greift anders als 60/min angenommen.\n")
        print("   kein 429 nach 80 Calls")
        return

    save("rate_limit_429.json", hit)
    body = json.dumps(hit["body"], ensure_ascii=False, default=str)
    m = re.search(r"try again in\s+(\d+)\s*second", body, re.I) or re.search(r"(\d+)\s*seconds", body, re.I)
    parsed = m.group(1) if m else None
    retry_after = hit["headers"].get("Retry-After") or hit["headers"].get("retry-after")
    print(f"   429 nach {hit['attempt']} Calls · geparst: {parsed} · Retry-After: {retry_after}")
    REPORT.append(f"- 429 nach **{hit['attempt']}** Calls ohne Bremse")
    REPORT.append(f"- Body: `{body[:200]}`")
    REPORT.append(f"- `Retry-After`-Header: `{retry_after}`")
    REPORT.append(f"- Vom Client-Muster geparst: **{parsed or 'NICHTS — Regex greift nicht'}** "
                  f"→ {'passt' if parsed else '`_retry_after_seconds()` in client.py anpassen'}\n")


# ----------------------------------------------------------------------------- Report
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rate-limit", action="store_true",
                    help="zusätzlich (4): fährt ins Rate-Limit, kostet ~60 Calls")
    args = ap.parse_args()

    if not KEY:
        sys.exit("DISCOVER_SWISS_KEY fehlt")

    os.makedirs(OUT, exist_ok=True)
    REPORT.append("# PROBE_OPEN — die offenen Fragen aus STOP-GATE P1\n")
    REPORT.append(f"Datum: {dt.date.today().isoformat()} · Project `{PROJECT}` · Basis `{BASE}`\n")

    count_field_seen: set = set()
    probe_contained_in_place(count_field_seen)
    probe_select_fields()
    report_count_field(count_field_seen)
    if args.rate_limit:
        probe_rate_limit()
    else:
        REPORT.append("## (4) Der echte 429-Body\n")
        REPORT.append("Nicht gemessen — `--rate-limit` war nicht gesetzt.\n")

    REPORT.append("## Konsequenzen für P2\n")
    REPORT.append("- (1) ✅ → `list_fallback()` bleibt wie gebaut, `containedInPlace` ist der Gebietsfilter.\n"
                  "- (1) ❌ → `list_fallback()` verliert den Gebietsparameter; der Fallback filtert nur noch "
                  "clientseitig über `geo`, und die Tool-Description muss sagen, dass ohne Koordinate keine "
                  "Regionsabgrenzung möglich ist.\n"
                  "- (2) → erlaubte Felder in `LIST_SELECT` (client.py) übernehmen, abgelehnte dort als "
                  "gemessen-verboten kommentieren.\n"
                  "- (3) → `_total_from()` kann auf den gemessenen Namen zeigen; tolerant bleibt es trotzdem.\n"
                  "- (4) → falls die Regex nicht greift, `_retry_after_seconds()` auf den echten Wortlaut ziehen.\n")
    REPORT.append(f"\n---\n\n{len(CALLS)} Calls. Rohantworten in `{OUT}/`.\n")

    save("calls.json", CALLS)
    with open("PROBE_OPEN_discover-swiss.md", "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT) + "\n")
    print(f"\n✔ PROBE_OPEN_discover-swiss.md + {OUT}/  ({len(CALLS)} Calls)")


if __name__ == "__main__":
    main()
