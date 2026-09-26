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

## Run locally with your own key

*Lokal ausführen mit eigenem Key.* Until discover.swiss has confirmed the
search entitlement in writing (README «Status»), there is no PyPI package and
no public instance. The server runs on your machine, with your own key, and
every call counts against your own quota.

**1. Key.** Self-service at [portal.discover.swiss](https://portal.discover.swiss/),
product *Infocenter Open*: 60 calls per minute, 50,000 per month. The key goes
into the environment, never into a file that gets committed. `.env` is
git-ignored; `.env.example` lists every variable with placeholders.

**2. Install** (Python 3.11–3.13):

```bash
git clone https://github.com/malkreide/discover-swiss-mcp.git
cd discover-swiss-mcp
python -m venv .venv
. .venv/bin/activate                  # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env                  # then put your key into .env
set -a; . ./.env; set +a
```

**3a. Claude Desktop (stdio).** In `claude_desktop_config.json`, with the
absolute path of the virtual environment's Python. This file stays on your
machine; the key in it is yours, never a committed value:

```json
{
  "mcpServers": {
    "discover-swiss": {
      "command": "/absolute/path/to/discover-swiss-mcp/.venv/bin/python",
      "args": ["-m", "discover_swiss_mcp"],
      "env": {
        "DISCOVER_SWISS_KEY": "your-subscription-key"
      }
    }
  }
}
```

The container variant, which takes the key from the environment Claude Desktop
starts in, is in [network-egress.md](network-egress.md).

**3b. Streamable HTTP on localhost.** Binds to `127.0.0.1:8000` and answers
under `/mcp`; no OAuth is needed on loopback, and any other bind address is
refused (SECURITY.md):

```bash
DISCOVER_SWISS_MCP_TRANSPORT=streamable-http python -m discover_swiss_mcp
```

Smoke check from a second shell. Protocol version 2026-07-28 needs more than a
plain `curl`, so use the SDK client that is already installed:

```bash
python - <<'PY'
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools])
            print((await s.call_tool("source_status", {})).content[0].text)

asyncio.run(main())
PY
```

Expected: the eight tool names, then `source_status` with
`"api_key_configured": true`, `"reachable": true` and an `entitlement_note`
that ends in «written confirmation from discover.swiss: pending». Without a key
it still answers (`api_key_configured: false`, a `hint`, no upstream call).

**4. The anchor query in four languages.** The rainy-day question (section 1)
is the query gate G1 will run over the public instance once the release is
cleared. Locally, anyone can run it now. The tool chain is the same in every
language; only `lang` changes, and the attribution per hit must be visible in
each answer:

| Language | Question | `lang` |
|---|---|---|
| DE | «Ich habe einen Regentag in Zürich — welche Museen sind in Gehdistanz zum HB, und wo esse ich danach vegetarisch?» | `de` |
| FR | «J'ai une journée de pluie à Zurich — quels musées sont à distance de marche de la gare centrale, et où manger végétarien ensuite?» | `fr` |
| IT | «Ho una giornata di pioggia a Zurigo — quali musei sono raggiungibili a piedi dalla stazione centrale, e dove mangio vegetariano dopo?» | `it` |
| EN | "I have a rainy day in Zurich — which museums are within walking distance of the main station, and where do I eat vegetarian afterwards?" | `en` |

Open point for step 3: the probe measured «vegetarisch» with the default
language only (136 hits, 2026-09-17). `lang` is sent as `Accept-Language`, and
the probe shows it translating names; whether full text matches a German term
under `fr`, `it` or `en`, or needs «végétarien», «vegetariano», «vegetarian»,
is not measured. A zero there is a question for the probe, not an answer that
Zurich has no vegetarian restaurant.

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
