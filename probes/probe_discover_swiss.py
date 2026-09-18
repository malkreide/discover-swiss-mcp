#!/usr/bin/env python3
"""
probe_discover_swiss.py — Live-Probe für discover.swiss Infocenter (Produkt «Infocenter Open»)
nach dem Skill mcp-data-source-probe, Schritt 1.

v4.1 (17.09.2026), nach Auswertung von Lauf 3 (Search-Envelope `values`, Paging `nextPageToken`):
- beide Projects (dsod-content, dsod-hs) werden vollständig geprobt
- Bestand je Endpoint via includeCount=true (Ground Truth ohne Paging)
- Gebietsfilter als Query-Parameter containedInPlace (nicht Header)
- /search: Rohantwort gespeichert; searchText, scoringReferencePoint (Geo), leafType, scheduleStart
- datasource-Filter (chm = SchweizMobil, zht-cms = Zürich Tourismus)
- Rohantwort der ersten Seite gespeichert (Envelope-Keys, Continuation-Feldname)

Nur Standardbibliothek. Aufruf (PowerShell):
    $env:DISCOVER_SWISS_KEY = "..."
    $env:PYTHONUTF8 = "1"
    python probe_discover_swiss.py --env prod

Budget: ~150 Calls, < 60/min, Abbruch bei 403 Quota.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASES = {"prod": "https://api.discover.swiss/info/v2", "test": "https://api.discover.swiss/test/info/v2"}
BASE = BASES["prod"]
UA = "swiss-public-data-mcp probe (https://github.com/malkreide)"
CALLS: list[dict] = []
RATE_WINDOW: list[float] = []
OUT_DIR = "probe_out"
SEL = "identifier,name,type,additionalType,license,copyrightNotice,dataGovernance,geo,containedInPlace"
REF_EPS = ("/amenities", "/categories", "/tags", "/areas", "/awards", "/projects")   # Referenzdaten, nicht Content
INTERLAKEN = "7.8632,46.6863"   # Longitude,Latitude — Format von scoringReferencePoint


# ----------------------------------------------------------------------------- HTTP
def _throttle() -> None:
    now = time.time()
    RATE_WINDOW[:] = [t for t in RATE_WINDOW if now - t < 60]
    if len(RATE_WINDOW) >= 55:
        wait = 60 - (now - RATE_WINDOW[0]) + 0.5
        print(f"   … Rate-Limit-Schutz: warte {wait:.0f}s", file=sys.stderr)
        time.sleep(max(wait, 0))
    RATE_WINDOW.append(time.time())


def call(path: str, key: str, *, params: dict | None = None, headers: dict | None = None,
         method: str = "GET", body: dict | None = None, label: str = ""):
    url = path if path.startswith("http") else f"{BASE}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    hdrs = {"Ocp-Apim-Subscription-Key": key, "User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
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
    if status == 429:
        m = re.search(r"(\d+) seconds", json.dumps(payload))
        wait = int(m.group(1)) + 1 if m else 61
        print(f"   429 — warte {wait}s und wiederhole", file=sys.stderr)
        time.sleep(wait)
        return call(path, key, params=params, headers=headers, method=method, body=body, label=label)
    if status == 403 and "quota" in json.dumps(payload).lower():
        print("\n!! HTTP 403 Quota Exceeded — Monatskontingent erschöpft. Abbruch.", file=sys.stderr)
        sys.exit(2)
    return status, payload, rh


def save(name: str, obj) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def rows_of(status: int, payload) -> list:
    if status != 200:
        return []
    if isinstance(payload, dict):
        for k in ("data", "values", "value", "results", "items"):
            if isinstance(payload.get(k), list):
                return payload[k]
        return []
    return payload if isinstance(payload, list) else []


def count_of(payload) -> int | None:
    """Gesamtzahl aus includeCount=true — Feldname unbekannt, daher tolerant."""
    if not isinstance(payload, dict):
        return None
    for k, v in payload.items():
        if isinstance(v, int) and re.search(r"count|total", k, re.I):
            return v
    return None


def cont_of(payload):
    """Listen-Endpoints: hasNextPage (bool) + nextPageToken (str). Nur den String-Token zurückgeben."""
    if not isinstance(payload, dict):
        return None
    for k in ("nextPageToken", "continuationToken", "continuation"):
        if isinstance(payload.get(k), str) and payload[k]:
            return payload[k]
    return None


def msg_of(payload) -> str:
    if isinstance(payload, dict):
        return str(payload.get("message") or payload.get("title") or payload)[:120]
    return str(payload)[:120]


# ----------------------------------------------------------------------------- Probes
def probe_openapi(key: str) -> dict:
    print("▶ 0. OpenAPI-Spec laden")
    st, spec, _ = call(f"{BASE}/openapi/v2.json", key, label="openapi")
    if st != 200 or not isinstance(spec, dict):
        print(f"   OpenAPI: HTTP {st} — {msg_of(spec)}")
        return {}
    save("openapi.json", spec)
    paths = spec.get("paths", {})
    list_eps = sorted(p for p in paths if p.count("/") == 1 and "{" not in p and "get" in paths[p])
    print(f"   {len(paths)} Pfade, davon {len(list_eps)} Listen-Endpoints")
    return {"spec_title": spec.get("info", {}).get("title"), "spec_version": spec.get("info", {}).get("version"),
            "list_endpoints": list_eps}


def probe_projects(key: str) -> list[dict]:
    print("▶ 1. Projects")
    st, pl, _ = call("/projects", key, params={"top": 50}, label="projects")
    projects = [p for p in rows_of(st, pl) if isinstance(p, dict) and p.get("identifier")]
    save("projects.json", projects)
    for p in projects:
        print(f"   {p.get('identifier'):16s} {p.get('name')}")
    return projects


def probe_matrix(key: str, project: str, eps: list[str]) -> list[dict]:
    print(f"▶ 2. Endpoint-Matrix für project={project} ({len(eps)} Endpoints; includeCount + erste Seite)")
    hdr = {"Accept-Language": "de", "categoryVersion": "sui"}
    results, raw_saved = [], False
    for ep in eps:
        r = {"project": project, "endpoint": ep, "http": None, "total": None, "first_page": 0, "cont_key": None,
             "licenses": collections.Counter(), "providers": collections.Counter(), "datasources": collections.Counter(),
             "types": collections.Counter(), "has_geo": 0, "sample": None, "note": ""}
        # (a) Bestand
        st, pl, _ = call(ep, key, params={"project": project, "top": 1, "includeCount": "true", "select": "identifier"},
                         headers=hdr, label=f"count/{project}{ep}")
        r["http"] = st
        if st != 200:
            r["note"] = msg_of(pl)
            print(f"   {ep:26s} HTTP {st}  {r['note'][:70]}")
            results.append(r)
            continue
        r["total"] = count_of(pl)
        if r["total"] is None and isinstance(pl, dict):
            r["note"] = f"includeCount ohne Zählfeld; Keys: {list(pl.keys())[:6]}"
        # (b) erste Seite für Lizenz-/Provider-Verteilung
        st, pl, _ = call(ep, key, params={"project": project, "top": 100, "select": SEL}, headers=hdr,
                         label=f"page/{project}{ep}")
        rows = rows_of(st, pl)
        r["first_page"] = len(rows)
        ck = [k for k in (pl.keys() if isinstance(pl, dict) else []) if re.search(r"contin|next", k, re.I)]
        r["cont_key"] = ck[0] if ck else None
        if rows and not raw_saved and ep not in REF_EPS:
            save(f"raw_first_page_{project}{ep.replace('/', '_')}.json", pl)
            raw_saved = True
        if rows:
            r["sample"] = rows[0]
            save(f"sample_{project}{ep.replace('/', '_')}.json", rows[:3])
        for o in rows:
            if not isinstance(o, dict):
                continue
            r["licenses"][str(o.get("license"))] += 1
            r["types"][f"{o.get('type')}/{o.get('additionalType')}"] += 1
            dg = o.get("dataGovernance") or {}
            prov = dg.get("provider") or {}
            r["providers"][prov.get("name") or prov.get("identifier") or "?"] += 1
            for org in dg.get("origin") or []:
                r["datasources"][f"{org.get('datasource')}:{org.get('license')}"] += 1
            if o.get("geo"):
                r["has_geo"] += 1
        print(f"   {ep:26s} HTTP {st}  total={str(r['total']):>6s}  seite1={r['first_page']:3d}  geo={r['has_geo']:3d}"
              f"  cont={r['cont_key']}  lic={dict(r['licenses'].most_common(2))}")
        results.append(r)
    return results


def probe_defaults(key: str, project: str, ep: str) -> list[tuple]:
    print(f"▶ 3. Default-Matrix auf {ep} (project={project})")
    out, hdr = [], {"categoryVersion": "sui", "Accept-Language": "de"}
    ids_seen = {}
    variants = [
        ("top weggelassen", {"project": project, "select": "identifier,name"}, hdr),
        ("top=5", {"project": project, "top": 5, "select": "identifier,name"}, hdr),
        ("top=1000", {"project": project, "top": 1000, "select": "identifier,name"}, hdr),
        ("Wiederholung top=5", {"project": project, "top": 5, "select": "identifier,name"}, hdr),
        ("project weggelassen", {"top": 5, "select": "identifier,name"}, hdr),
        ("Accept-Language fehlt", {"project": project, "top": 3}, {"categoryVersion": "sui"}),
        ("Accept-Language=en", {"project": project, "top": 3}, {**hdr, "Accept-Language": "en"}),
        ("Accept-Language=fr", {"project": project, "top": 3}, {**hdr, "Accept-Language": "fr"}),
        ("Accept-Language=it", {"project": project, "top": 3}, {**hdr, "Accept-Language": "it"}),
        ("categoryVersion fehlt", {"project": project, "top": 3}, {"Accept-Language": "de"}),
        ("deleted=true", {"project": project, "top": 3, "deleted": "true"}, hdr),
        ("select weggelassen", {"project": project, "top": 3}, hdr),
        ("datasource=zht-cms", {"project": project, "top": 1, "includeCount": "true", "datasource": "zht-cms"}, hdr),
        ("datasource=chm", {"project": project, "top": 1, "includeCount": "true", "datasource": "chm"}, hdr),
        ("datasource=ctd-vgl", {"project": project, "top": 1, "includeCount": "true", "datasource": "ctd-vgl"}, hdr),
        ("updatedSince=2026-09-01", {"project": project, "top": 1, "includeCount": "true",
                                     "updatedSince": "2026-09-01T00:00:00"}, hdr),
    ]
    for label, params, headers in variants:
        st, pl, _ = call(ep, key, params=params, headers=headers, label=f"default/{label}")
        rows = rows_of(st, pl)
        ids_seen[label] = [o.get("identifier") for o in rows if isinstance(o, dict)][:5]
        first = rows[0].get("name") if rows and isinstance(rows[0], dict) else None
        total = count_of(pl)
        out.append((label, st, len(rows), total, bool(cont_of(pl)), str(first)[:45], CALLS[-1]["bytes"]))
        print(f"   {label:26s} HTTP {st}  rows={len(rows):4d}  total={str(total):>6s}  cont={bool(cont_of(pl))!s:5s}"
              f"  {CALLS[-1]['bytes']:7d}B  first={str(first)[:30]}")
    stable = ids_seen.get("top=5") == ids_seen.get("Wiederholung top=5")
    out.append(("Ordnung stabil (top=5 zweimal)", "-", "-", "-", "-", str(stable), 0))
    print(f"   Ordnung stabil: {stable}")
    return out


def probe_search(key: str, project: str) -> list[tuple]:
    print(f"▶ 4. /search (project={project})")
    out = []
    tests = [
        ("leer, top 3", {"project": [project], "resultsPerPage": 3, "select": "identifier,name,type,leafType"}),
        ("searchText=Landesmuseum", {"project": [project], "searchText": "Landesmuseum", "resultsPerPage": 5,
                                     "select": "identifier,name,type"}),
        ("searchText=Grindelwald", {"project": [project], "searchText": "Grindelwald", "resultsPerPage": 5,
                                    "select": "identifier,name,type"}),
        ("searchText=Wanderung", {"project": [project], "searchText": "Wanderung", "resultsPerPage": 5,
                                  "select": "identifier,name,type"}),
        ("Geo: Interlaken, Hotels", {"project": [project], "leafType": ["Hotel"], "scoringReferencePoint": INTERLAKEN,
                                     "resultsPerPage": 5, "select": "identifier,name,address"}),
        ("Geo: Interlaken, alles", {"project": [project], "scoringReferencePoint": INTERLAKEN, "resultsPerPage": 5,
                                    "select": "identifier,name,type,leafType"}),
        ("Events ab heute", {"project": [project], "type": ["Event"], "scheduleStart": dt.date.today().isoformat(),
                             "resultsPerPage": 5, "select": "identifier,name,type"}),
        ("Facets leafType", {"project": [project], "facets": ["leafType"], "resultsPerPage": 1, "select": "identifier"}),
        ("ohne project", {"searchText": "Landesmuseum", "resultsPerPage": 3, "select": "identifier,name"}),
    ]
    for i, (label, body) in enumerate(tests):
        st, pl, _ = call("/search", key, method="POST", body=body, headers={"Accept-Language": "de"},
                         label=f"search/{label}")
        save(f"search_{project}_{i}.json", pl)
        rows = rows_of(st, pl)
        total = count_of(pl)
        names = [str(o.get("name"))[:28] for o in rows[:3] if isinstance(o, dict)]
        info = f"rows={len(rows)} total={total} {names}" if st == 200 else msg_of(pl)
        if st == 200 and isinstance(pl, dict) and i == 0:
            info += f" | keys={list(pl.keys())[:8]}"
        out.append((label, st, info[:160]))
        print(f"   {label:26s} HTTP {st}  {info[:110]}")
    return out


def probe_areas(key: str, project: str, results: list[dict]) -> list[tuple]:
    print(f"▶ 5. Gebiete und Gebietsfilter (Query-Parameter containedInPlace), project={project}")
    out, areas, cont, page = [], [], None, 0
    while page < 6:
        st, pl, _ = call("/areas", key, params={"project": project, "top": 100, "continuationToken": cont,
                                                "select": "identifier,name,additionalType"},
                         headers={"Accept-Language": "de"}, label="areas")
        areas += rows_of(st, pl)
        cont = cont_of(pl)
        page += 1
        if not cont:
            break
    save(f"areas_{project}.json", areas)
    wanted = {"Zürich": None, "Interlaken": None, "Luzern": None, "Grindelwald": None, "Bern": None, "Glarus": None}
    for a in areas:
        for w in wanted:
            if wanted[w] is None and str(a.get("name", "")) == w:
                wanted[w] = a.get("identifier")
    for a in areas:   # zweite Runde: startswith
        for w in wanted:
            if wanted[w] is None and str(a.get("name", "")).startswith(w):
                wanted[w] = a.get("identifier")
    print(f"   /areas: {len(areas)} Gebiete ({page} Seiten); " + ", ".join(f"{k}={v}" for k, v in wanted.items()))
    out.append(("GET /areas", st, f"{len(areas)} rows; " + json.dumps(wanted, ensure_ascii=False)))
    content = [r for r in results if r["http"] == 200 and (r["total"] or r["first_page"]) and r["endpoint"] not in REF_EPS]
    for ep in [r["endpoint"] for r in sorted(content, key=lambda r: -(r["total"] or r["first_page"]))[:2]]:
        for w, aid in wanted.items():
            if not aid:
                continue
            st, pl, _ = call(ep, key, params={"project": project, "top": 1, "includeCount": "true",
                                              "containedInPlace": aid, "select": "identifier,name"},
                             headers={"categoryVersion": "sui"}, label=f"area/{w}{ep}")
            total = count_of(pl)
            out.append((f"{ep} containedInPlace={w} ({aid})", st, f"total={total}" if st == 200 else msg_of(pl)))
            print(f"   {ep:22s} in {w:12s}: HTTP {st}  total={total}")
    return out


# ----------------------------------------------------------------------------- Report
def write_report(path: str, oa: dict, projects: list[dict], matrices: dict, defaults: dict, searches: dict, areas: dict):
    today = dt.date.today().isoformat()
    L = [f"# PROBE_REPORT — discover-swiss-mcp (v4)\n",
         f"**Probe-Datum:** {today} · **Produkt:** Infocenter Open · **Basis:** `{BASE}` · **Calls:** {len(CALLS)} · "
         f"**Spec:** {oa.get('spec_title')} {oa.get('spec_version')}\n",
         "**Status:** Schritt 1 automatisch erhoben, beide Projects. Offen: 1.4b Recall-Ground-Truth (manuell), "
         "Lizenz-Rückfrage discover.swiss, Architektur-Entscheid (Schritt 2).\n", "---\n", "## 1. Projects\n",
         "| ID | Name |\n|---|---|"]
    L += [f"| `{p.get('identifier')}` | {p.get('name')} |" for p in projects]
    for pj, res in matrices.items():
        L.append(f"\n## 2. Befund-Tabelle — project=`{pj}`\n")
        L.append("| Endpoint | HTTP | Status | Bestand (includeCount) | Seite 1 | geo | Continuation-Feld | Bemerkung |\n|---|---|---|---|---|---|---|---|")
        for r in res:
            n = r["total"] if r["total"] is not None else r["first_page"]
            status = "✅" if r["http"] == 200 and n else ("⚠️ leer" if r["http"] == 200 else "❌")
            L.append(f"| `{r['endpoint']}` | {r['http']} | {status} | {r['total']} | {r['first_page']} | {r['has_geo']} | "
                     f"{r['cont_key']} | {r['note']} |")
        L.append(f"\n### 2.1 Lizenzen, Provider, Datasources, Typen (Seite 1) — project=`{pj}`\n")
        for r in res:
            if r["first_page"] == 0 or r["endpoint"] in REF_EPS:
                continue
            L.append(f"- `{r['endpoint']}` — Lizenz (root): " + ", ".join(f"{k}: {v}" for k, v in r["licenses"].most_common(6))
                     + "\n  Provider: " + ", ".join(f"{k}: {v}" for k, v in r["providers"].most_common(8))
                     + "\n  Datasource:Lizenz: " + ", ".join(f"{k}: {v}" for k, v in r["datasources"].most_common(10))
                     + "\n  Typen: " + ", ".join(f"{k}: {v}" for k, v in r["types"].most_common(6)))
    for pj, d in defaults.items():
        L.append(f"\n## 3. Default-Matrix — project=`{pj}`\n\n| Variante | HTTP | Rows | total | cont | erstes Objekt | Bytes |\n|---|---|---|---|---|---|---|")
        L += [f"| {a} | {b} | {c} | {d_} | {e} | {f} | {g} |" for a, b, c, d_, e, f, g in d]
    for pj, s in searches.items():
        L.append(f"\n## 4. /search — project=`{pj}`\n\n| Test | HTTP | Ergebnis |\n|---|---|---|")
        L += [f"| {a} | {b} | {c} |" for a, b, c in s]
    for pj, a_ in areas.items():
        L.append(f"\n## 5. Gebiete und Gebietsfilter — project=`{pj}`\n\n| Call | HTTP | Ergebnis |\n|---|---|---|")
        L += [f"| {a} | {b} | {c} |" for a, b, c in a_]
    L.append("\n## 6. Manuell zu ergänzen\n")
    L += ["- [ ] **1.4b Recall-Ground-Truth**: `Landesmuseum`, `Grindelwald`, `Wanderung` — Trefferzahlen gegen zuerich.com / "
          "myswitzerland.com / schweizmobil.ch vergleichen, Delta erklären",
          "- [ ] **Lizenz-Filter**: Anteil `C-All-Rights-Reserved` an root-`license` je Endpoint → Server muss filtern oder flaggen",
          "- [ ] **Search-Berechtigung**: Doku sagt «kein Search für Open» — Befund in Abschnitt 4 dagegenhalten; falls 200: schriftlich bei discover.swiss bestätigen lassen",
          "- [ ] **Architektur-Entscheid** (Schritt 2)"]
    L.append("\n## 7. Call-Protokoll\n\n| # | Label | HTTP | ms | Bytes |\n|---|---|---|---|---|")
    L += [f"| {i} | {c['label']} | {c['status']} | {c['ms']} | {c['bytes']} |" for i, c in enumerate(CALLS, 1)]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    save("calls.json", CALLS)
    print(f"\n✔ Report: {path}   Rohdaten: {OUT_DIR}/   Calls: {len(CALLS)}")


# ----------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", default=os.environ.get("DISCOVER_SWISS_KEY"))
    ap.add_argument("--env", choices=list(BASES), default=os.environ.get("DISCOVER_SWISS_ENV", "prod"))
    ap.add_argument("--projects", default="", help="Kommaliste; Default: alle aus /projects")
    ap.add_argument("--endpoints", default="", help="Kommaliste, überschreibt OpenAPI-Auswahl")
    ap.add_argument("--out", default="PROBE_REPORT_discover-swiss-mcp.md")
    a = ap.parse_args()
    if not a.key:
        sys.exit("DISCOVER_SWISS_KEY fehlt (env oder --key).")
    global BASE
    BASE = BASES[a.env]
    print(f"Umgebung: {a.env.upper()}  →  {BASE}")

    oa = probe_openapi(a.key)
    eps = [e.strip() for e in a.endpoints.split(",") if e.strip()] or oa.get("list_endpoints") or ["/places"]
    eps = [e for e in eps if e not in ("/search", "/timezones", "/vertices", "/openapi", "/status", "/projects")]
    projects = probe_projects(a.key)
    pids = [p.strip() for p in a.projects.split(",") if p.strip()] or [p["identifier"] for p in projects] or ["dsod-content"]

    matrices, defaults, searches, areas = {}, {}, {}, {}
    for pj in pids:
        matrices[pj] = probe_matrix(a.key, pj, eps)
        content = [r for r in matrices[pj] if r["http"] == 200 and (r["total"] or r["first_page"]) and r["endpoint"] not in REF_EPS]
        if not content:
            print(f"   (project={pj}: keine Content-Endpoints mit Daten — Default-Matrix/Search übersprungen)")
            searches[pj] = probe_search(a.key, pj)
            continue
        best = max(content, key=lambda r: (r["total"] or r["first_page"]))["endpoint"]
        defaults[pj] = probe_defaults(a.key, pj, best)
        searches[pj] = probe_search(a.key, pj)
        areas[pj] = probe_areas(a.key, pj, matrices[pj])
    write_report(a.out, oa, projects, matrices, defaults, searches, areas)


if __name__ == "__main__":
    main()
