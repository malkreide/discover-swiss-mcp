# Demo — the three anchor queries, step by step

The three questions from the probe report (section 8), each as the tool chain
an assistant is expected to run: which tool, in which order, with which
parameters, and what to check in the answer. Anyone with a subscription key
can reproduce them — through an MCP host, or directly with
`python scripts/p2_anchor_run.py`, which calls the same `*_impl` functions
with these parameters (about ten calls). That script predates `webcams_near`
and looks the Braunwald webcams up through `search(types=["Webcam"])`; the
hits are the same, only the `live_url`/`snapshot_url` labelling is missing.

```bash
export DISCOVER_SWISS_KEY="your-subscription-key"   # never in a committed file
python scripts/p2_anchor_run.py
```

Coordinates used below (WGS84):

| Place | `lat` | `lon` |
|---|---|---|
| Zurich main station (HB) | 47.3779 | 8.5403 |
| Braunwald | 46.9404 | 8.9995 |
| Interlaken | 46.6863 | 7.8632 |

What holds for every step: each hit carries `attribution` (provider, licence,
copyright notice), and the assistant shows it with the content. An empty
result carries a `hint`; the assistant follows it instead of concluding that
nothing exists. `degraded` set means *no measurement*, not *no result*.

---

## 1. City — rainy day in Zurich

> *"I have a rainy day in Zurich — which museums are within walking distance
> of the main station, and where do I eat vegetarian afterwards?"*

| Step | Tool | Parameters | Why |
|---|---|---|---|
| 1 | `search` | `types=["Museum"]`, `near={lat: 47.3779, lon: 8.5403}`, `radius_km=1.5` | Museums with a hard 1.5 km cut-off, ranked by distance; each hit has `distance_km` |
| 2 | `get_details` | `identifier=<first hit>` (Landesmuseum: `civ_px9-s28_bggg`) | Opening hours, admission (`fees`), Zürich Card, accessibility; description as plain text |
| 3 | `search` | `query="vegetarisch"`, `types=["Restaurant"]`, `near={lat: 47.3779, lon: 8.5403}` | `match` stays `all`: «vegetarisch» is in descriptions, not in names (136 vs. 0 on 2026-09-17) |

**Check in the answer:**
- Provider Zürich Tourismus, licence CC BY-SA, notice «Zürich Tourismus
  www.zuerich.com» — shown with the museums and restaurants.
- Step 2 carries a `disclaimer` (opening hours and prices without guarantee).
  The assistant passes it on.
- Step 3 ranks by text relevance first, distance second (a restaurant at
  0.6 km can rank behind one at 3.5 km). If walking distance matters, the
  assistant adds `radius_km`.

---

## 2. Outdoor — Braunwald, Glarnerland

> *"I'm in Braunwald: which hikes with little ascent are there, what does the
> webcam show right now, and is anything closed?"*

| Step | Server | Tool | Parameters | Why |
|---|---|---|---|---|
| 1 | discover-swiss-mcp | `find_tours` | `near={lat: 46.9404, lon: 8.9995}`, `radius_km=10`, `ascent_m_max=300` | Tours near Braunwald with at most 300 m ascent; hits carry `length_km`, `ascent_m`, `difficulty` |
| 1b | discover-swiss-mcp | `find_tours` | `region="Glarnerland"`, `kind="hiking"` | Wider net if step 1 is thin; `area` in the answer shows the resolved id (`ds_glarnerland`) |
| 2 | discover-swiss-mcp | `webcams_near` | `near={lat: 46.9404, lon: 8.9995}`, `radius_km=15` | `live_url` is the live image; `snapshot_url` is a stored still and says so |
| 3 | swiss-tourism-mcp | `trail_closures` | around Braunwald | Closures are not in discover.swiss |
| 4 | swiss-tourism-mcp | `cable_cars_near` | around Braunwald | Braunwald is car-free; the funicular is the way up |
| 5 | meteoswiss-mcp | forecast for Braunwald | | Weather is not in discover.swiss |

**Check in the answer:**
- `ascent_m_max` only keeps tours that *declare* an ascent. RailAway products
  carry none and drop out; the tool description says so, and the assistant
  must not claim the list is complete.
- The webcam image is labelled: live link versus stored snapshot.
- Closure information comes from swiss-tourism-mcp with its own safety
  disclaimer — discover.swiss says nothing about closures, and silence from it
  is not an all-clear.

---

## 3. Lodging — near Interlaken, nationwide coverage

> *"Family-friendly hotel near Interlaken, three stars, accessible — and how
> do I get there from Zurich airport?"*

| Step | Server | Tool | Parameters | Why |
|---|---|---|---|---|
| 1 | discover-swiss-mcp | `find_accommodation` | `near={lat: 46.6863, lon: 7.8632}`, `radius_km=5`, `stars_min=3`, `accessible=true` | Hotels within 5 km, at least three stars, with an accessibility profile from Pro Infirmis or OK:GO |
| 2 | discover-swiss-mcp | `get_details` | `identifier=<first hit>`, `lang="en"` | Accessibility profile names, amenities, check-in/out, rooms |
| 3 | swiss-transport-mcp | connection | from Zürich Flughafen to Interlaken Ost | Journey is not in discover.swiss |

**Check in the answer:**
- **"Family-friendly" is not a filter.** No amenity name for it was found in
  the recorded index. The assistant reads the amenities from step 2 and says
  what they show — it does not assert family-friendliness the data does not
  state.
- `accessible=true` narrows to about 1,000 of 5,275 lodgings nationwide. If
  the result is thin, the `hint` says to drop `accessible` before concluding
  there is nothing.
- No nightly prices and no availability: the answer says so and points to the
  provider or a booking channel.
- Hotels in the Bernese Oberland are covered; sights and hikes there are not.
  A follow-up "what can we do in Interlaken?" gets a scope answer, not an
  invented one.

---

## Reproducing the counts

The live canaries in `tests/test_live.py` hold the numbers these demos depend
on — hotels within 5 km of Interlaken ≥ 40, Glarnerland tours ≥ 50, webcams
around St. Gallen, the Landesmuseum detail without HTML entities:

```bash
pytest -m live -rA
```
