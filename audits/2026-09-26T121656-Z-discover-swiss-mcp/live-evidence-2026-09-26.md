# Live evidence, 2026-09-26 (maintainer's machine)

Both runs were executed by the maintainer with a real subscription key on
Windows, Python 3.14.7, against `main` at the state that contains commit
`f326260`. The sandbox of the re-audit cannot reach the API (outbound
connections by IP are blocked), so these runs are the live evidence for the
checks that require one. Transcribed from the console output the maintainer
pasted into the session; the original files stay on that machine.

## `pytest -m live -rA` — 24 passed, 1 skipped

| Canary | Measured | Floor |
|---|---:|---:|
| search('Landesmuseum').upstream_count | 52 | 20 |
| search('Grindelwald').upstream_count | 37 | 15 |
| search('Wanderung').upstream_count | 533 | 200 |
| find_accommodation(near Interlaken).upstream_count | 5277 | 2000 |
| find_accommodation(near Interlaken, 5 km).upstream_count | 83 | 40 |
| find_tours().upstream_count | 223 | 100 |
| find_tours(region='Glarnerland').upstream_count | 117 | 50 |
| find_tours(length_km_max=10).upstream_count | 29 | 10 |
| webcams_near(St. Gallen, 100 km).upstream_count | 73 | 30 |
| webcams_near(St. Gallen, 25 km).upstream_count | 18 | 8 |
| explore_area().total | 20848 | 15000 |
| search(sourcePartner=zht).count | 1307 | 600 |
| find_events(today..+365 d).upstream_count | 16 | 5 |
| search('Landesmuseum') name vs all | 7 < 52 | ≥ 3 and less |
| explore_area facet containedInPlace/id | key present | key present |
| get_details(Landesmuseum).description | «Das Landesmuseum gleich beim Zürcher Hauptbahnhof …», no entity | Hauptbahnhof, no entity |
| find_accommodation(near Interlaken).hits[0] | Hotel Du Nord / Interlaken | Interlaken |
| status().reachable | True | True |
| source_status | reachable, search available, index_total 20848 | ≥ 15000 |
| list civicStructures / foodEstablishments / localbusinesses / lodgingbusinesses / places | 1406 / 1439 / 1590 / 5277 / 447 | 700 / 700 / 790 / 2600 / 224 |

Skipped: `test_demo_event_is_filtered_and_counted` — `excluded_test_objects == 0`
in the default 30-day window. Not a result: the canary cannot tell a removed
record from one outside the window (fixed after this run: it now looks the
record up by name).

Wire details visible in the log: `GET /vertices/…?project=dsod-content&includeAllPhotos=false`
answered 200; the list calls with the 15-field `select` answered 200.

## `python probes/probe_query_syntax.py` — see `probes/PROBE_QUERY_discover-swiss.md`
