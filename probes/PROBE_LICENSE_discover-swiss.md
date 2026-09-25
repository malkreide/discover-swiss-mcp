# PROBE_LICENSE — die Lizenz eines Suchtreffers

Datum: 2026-09-25 · Project `dsod-content` · Skript `probes/probe_license.py` · rund 20 Calls

## Anlass

Der erste Live-Lauf der P2-Tools (`scripts/p2_anchor_run.py`, 25.09.) lieferte bei allen sechs Suchen `returned=0`; sämtliche Treffer standen in `excluded_by_license`. Die Filter selbst griffen (26 Museen ≤ 1.5 km HB, 8 Hotels, 9 Touren, `ds_glarnerland` aufgelöst).

Ursache: Suchtreffer tragen weder ein root-`license` (nicht in `IndexResponse`) noch `dataGovernance.provider` — nur die Liste `origin`. Die Regel aus P1 suchte die Herkunft des Besitzers über `provider` und fand ohne ihn keine.

## Befund

Je drei Treffer aus fünf Typen; verglichen mit dem root-`license` des Detail-Objekts (`/vertices/{id}`), das verbindlich ist.

| Typ | Beispiel | root | `hit.datasource` | Regel `datasource` | Regel «erste Herkunft» |
|---|---|---|---|---|---|
| Museum | `civ_px9-s28_babcbig` | CC BY-SA | `zht-cms` | ✅ | ✅ |
| Museum | `civ_px9-s28_bhbi` Musée Visionnaire | CC BY-SA | `zht-cms`, `gdl`, `gin` | ❌ (+ C-All-Rights-Reserved) | ✅ |
| Museum | `civ_px9-s28_bgce` | CC BY-SA | `zht-cms`, `gdl`, `gin` | ❌ (+ CC-BY-ND-SA) | ✅ |
| Hotel | `log_x8-tdgf_bceea` | CC BY | `hs-d365`, `hs-my`, `hs`, `hcl`, `st-sc` | ❌ | ✅ |
| Hotel | `log_x8-tdgf_bbbei` | CC BY | `hs-d365`, `hs`, `hcl`, `st-sc` | ❌ (+ C All-Rights-Reserved) | ✅ |
| Hotel | `log_x8-tdgf_baaii` | CC BY | wie oben | ❌ | ✅ |
| Tour ×3 | `tou_s9t_…` | CC BY-SA | `ctd-tht` | ✅ | ✅ |
| Webcam ×3 | `web_s9t_…` | CC BY-SA | `ctd-ltm`, `ctd-hlt` | ✅ | ✅ |
| HotelRoom ×3 | `hs-my_…` | CC BY | `hs-my` | ✅ | ✅ |

**Übereinstimmung mit dem root-Lizenzfeld: Regel `datasource` 10 / 15, Regel «erste Herkunft» 15 / 15.**

Gegenprobe über alle 105 aufgezeichneten Objekte mit root-`license` in `probes/`: «erste Herkunft» 105 / 105 (Test `test_first_origin_equals_the_root_licence_in_every_recorded_object`).

## Nebenbefunde

1. **`hit.datasource` listet alle Herkünfte**, nicht die des Besitzers — als Lizenzquelle unbrauchbar.
2. **contentdesk heisst als Provider `tso-ctd`, die Datenquellen aber `ctd-tht`, `ctd-hlt`, `ctd-ltm`, `ctd-sgt`.** Die P1-Regel «Datenquelle beginnt mit dem Provider-Kürzel» hätte Touren und Webcams auch mit `provider` nie gefunden.
3. **Besitzer ≠ erste Herkunft ≠ Fehler.** Bei den TOMAS-Zimmern ist `provider` = `tom` (CC BY-ND), die erste Herkunft `hs-my` (CC BY) — und das root-Lizenzfeld ist ebenfalls CC BY. Massgebend ist die Lizenz, nicht der Name des Besitzers.
4. **Lizenz-Schreibweisen:** `C All-Rights-Reserved` (mit Leerzeichen) und `CC-BY-ND-SA` kommen vor; beide normalisieren nicht in die Whitelist.

## Konsequenz

`licenses.license_of`: root-`license`, sonst Lizenz der ersten Herkunft. Beibehalten wird eine Sperre: Nennt ein Objekt einen Provider, aber keine Herkunft dieses Providers, wird nichts geraten. Die Attribution nennt bei Suchtreffern den Provider der ersten Herkunft.
