# PROBE_TOURKINDS — womit sich Tourenarten trennen lassen

Datum: 2026-09-25 · Project `dsod-content` · Skript `probes/probe_tour_kinds.py` · 11 Calls

## Anlass

Live-Lauf der P2-Tools (25.09.): `find_tours(region="Glarnerland", kind="hiking")` lieferte als erste Treffer zwei Schneeschuhtouren. Die Zuordnung `kind` → `leafType` aus P2 war nicht gemessen, sondern angenommen.

## Befund 1 — welche Werte es gibt (Facetten über `type=Tour`, 223 Touren)

**leafType:** ThemeTrail 88 · Route 45 · NatureTrail 23 · Tour 16 · CrossCountry 9 · TobogganRun 8 · ViaFerrata 8 · ShipTour 7 · SkiSlope 4 · HikingTrail 3 · TrainTour 3 · BikeTrail 2 · Way 2 · CarTour 1 · GlacierTour 1 · HighTour 1 · Longdistance 1 · SegwayTour 1

**Nicht vorhanden:** `CyclingRoute`, `MountainBikeRoute`, `SnowshoeTrail` — drei der fünf Werte, die die P2-Zuordnung sendete. `kind="cycling"` und `kind="mtb"` lieferten dadurch immer eine Leermenge, `kind="winter"` verlor alle 23 Schneeschuhtouren. Ohne Fehlermeldung.

**categoryTree (Auszug):** Zu Fuss 40 (Wandern 37, Spazieren 2, Weitwandern 2) · Wintersport 35 (Schneeschuhwandern 23, Langlaufen 6, Schlitteln 4, Skitour 1, Winterwandern 1) · Velofahren 2 (E-Mountainbike 2, Mountainbike 2, E-Bike 1, Fahrrad 1)

**tag (Auszug):** seasonality-winter 37 · seasonality-summer 28 · month-* 7–20 je Monat

## Befund 2 — Filterverhalten

| Fall | Body | count |
|---|---|---:|
| A | leafType = 7 Wander-Typen | 178 |
| B | categoryTree = `sui_root|sui_01|sui_0110` (voller Pfad) | 35 |
| C | categoryTree = `sui_0110` (Kurzform) | **0** |
| D | categoryTree Velofahren, voller Pfad | 2 |
| E | categoryTree Mountainbike, voller Pfad | 2 |
| F | categoryTree Zu Fuss, voller Pfad | 40 |
| G | leafType CrossCountry, TobogganRun, SkiSlope | 21 |
| H | A **und** B | 25 |
| I | A + season `jul` | **20** |
| J | leafType BikeTrail | 2 |

1. **`categoryTree` filtert nur mit dem vollen Pfad.** Die Kurzform liefert still 0.
2. **`leafType` und `categoryTree` werden UND-verknüpft** (H 25 < A 178). Eine Art «Typ ODER Kategorie» ist im Body nicht ausdrückbar.
3. **`season` behält nur Touren mit Saisonangabe:** 20 von 178 Wandertouren für Juli. Ein Saisonfilter schneidet still den grössten Teil weg.
4. `ThemeTrail` umfasst auch Velo-Anlässe («Velo-Rallye Bodensee»): Die Einordnung folgt dem Anbieter.

## Konsequenz

| `kind` | Filter | Treffer (gesamt) |
|---|---|---:|
| hiking | leafType HikingTrail, Route, Way, Tour, Longdistance, NatureTrail, ThemeTrail | 178 (davon 25 als Wintersport kategorisiert) |
| winter | categoryTree `sui_root|sui_01|sui_0110` | 35 |
| cycling | categoryTree `sui_root|sui_01|sui_0102` | 2 |
| mtb | categoryTree `sui_root|sui_01|sui_0102|sui_010205` | 2 |
| theme | leafType ThemeTrail, NatureTrail | 111 |

Tool-Description und Leermengen-Hint von `find_tours` sagen jetzt, dass `kind` der Einordnung des Anbieters folgt und dass jeder Filter nur Touren trifft, die den Wert tragen — `season_month` zuerst weglassen.
