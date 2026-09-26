> 🇨🇭 **Part of the [Swiss Public Data MCP Portfolio](https://github.com/malkreide)**

# discover-swiss-mcp

<!-- mcp-name: io.github.malkreide/discover-swiss-mcp -->

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io/)
[![Key required](https://img.shields.io/badge/auth-bring%20your%20own%20key-orange)](https://portal.discover.swiss/)

> MCP server for discover.swiss Infocenter Open — search Swiss tourism data with per-object attribution

🇩🇪 [Deutsche Version](README.de.md)

---

## Status

**pre-release — search entitlement confirmation from discover.swiss: pending.**

| Item | State |
|---|---|
| Search entitlement (written confirmation by discover.swiss) | **pending** — release gate |
| Tools | all eight registered (P3), live canaries in place (P4) |
| Release | none; version 0.1.0 is not published |

The live probe of 2026-09-17 found that `/search` works for the Open
subscription — full text, distance ranking, date filters, 31 facets — although
the official documentation states the opposite ("You can't use the search
functionality"). The whole server is built on that endpoint, which makes the
contradiction its main risk: an entitlement that contradicts the docs can be
withdrawn without notice.

- Written confirmation from discover.swiss is a **release gate**. No release
  before that conversation has happened. Once it has, set
  `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED=YYYY-MM-DD` and this section changes
  from *pending* to *confirmed* with that date.
- `source_status` reports the same state at runtime, so a host can see it
  without reading this file.
- If the entitlement is withdrawn, the server keeps answering through a
  narrower list fallback (see *Architecture decision*).

---

## Anchor demo queries

Three questions this server is built to answer, chosen to fit the coverage it
actually has. The tool chain for each — which tool, in which order, with which
parameters — is in [docs/DEMO.md](docs/DEMO.md), reproducible by anyone with a
key.

1. **City (Zurich pilot)** — *"I have a rainy day in Zurich — which museums are
   within walking distance of the main station, and where do I eat vegetarian
   afterwards?"* `search` → `get_details` → `search`; Zürich Tourismus as the
   source (CC BY-SA), attribution visible.
2. **Outdoor (Glarnerland)** — *"I'm in Braunwald: which hikes with little
   ascent are there, what does the webcam show right now, and is anything
   closed?"* `find_tours` → `webcams_near`, together with `swiss-tourism-mcp`
   (closures, cable cars) and `meteoswiss-mcp` (weather). Shows two servers
   working together.
3. **Lodging (nationwide)** — *"Family-friendly hotel near Interlaken, three
   stars, accessible — and how do I get there from Zurich airport?"*
   `find_accommodation` with distance ranking → `get_details`, then
   `swiss-transport-mcp` for the journey.

---

## Scope map

What the open index holds, counted live on **2026-09-17**
(`probes/PROBE_REPORT_discover-swiss-mcp.md`). 20,817 objects in total.

| In scope | Count | Note |
|---|---:|---|
| Lodging businesses, **nationwide** | 5,275 | Zermatt to Geneva; HotellerieSuisse, Schweiz Tourismus, TOMAS, contentdesk |
| Hotel rooms and meeting rooms | 10,112 rooms | excluded from `search` unless `types` asks for them |
| Points of interest — Zurich (Zürich Tourismus) | 1,311 | museums, restaurants, shops, nightlife |
| Points of interest — Eastern Switzerland | 6,211 | Glarnerland 1,752 · Thurgau 1,381 · St. Gallen-Bodensee 1,338 · Heidiland 711 · Appenzellerland 608 · Toggenburg 421 |
| Liechtenstein · Engadin Scuol | 553 · 429 | |
| Tours | 223 | Eastern Switzerland, Zurich region; 16 from SchweizMobil |
| Webcams | 73 | all in Eastern Switzerland |
| Ski resorts · cable cars and lifts | 21 · 36 | |

| Not in scope | Why it matters |
|---|---|
| Points of interest, tours, webcams for the **Bernese Oberland, Central Switzerland, Valais, Ticino, Romandie** | Hotels there are covered; sights, restaurants and hikes are not. An empty answer there means *no data*, not *nothing there*. |
| **Events** | 21 entries in the whole index, a test record among them — practically empty. `find_events` says so in its description. |
| **Nightly prices** | Only a provider-declared price band (Niedrig / Mittel / Hoch). |
| **Availability** | Not in the Infocenter product. |
| **Booking** | Marketplace product, not this server. |

`explore_area` and `source_status` report this coverage at runtime, so a model
can check it before it searches.

---

## Features

- **8 read-only tools** over search, detail, accommodation, tours, events,
  webcams, area exploration and source status
- **Per-object attribution** — provider, licence and copyright notice travel in
  the response, not in this README
- **Licence whitelist** on the root `license` field; everything else is counted
  into `excluded_by_license` and never served
- **Empty results carry a reason** — a `hint` naming what to change, never an
  unexplained empty list
- **Degraded states are named** — `quota_exhausted`, `upstream_unreachable`,
  `search_unavailable`
- **Dual transport** — stdio (Claude Desktop) and Streamable HTTP (cloud)

---

## Prerequisites

- Python 3.11, 3.12 or 3.13
- A discover.swiss Infocenter Open subscription key (self-service at
  [portal.discover.swiss](https://portal.discover.swiss/)) — bring your own key
- Rate limits of that subscription: 60 calls/minute, 50,000 calls/month

---

## Installation

```bash
git clone https://github.com/malkreide/discover-swiss-mcp.git
cd discover-swiss-mcp
pip install -e ".[dev]"
```

---

## Usage / Quickstart

```bash
export DISCOVER_SWISS_KEY="your-subscription-key"

# stdio (Claude Desktop and other local clients)
python -m discover_swiss_mcp

# Streamable HTTP — binds to 127.0.0.1:8000 by default (localhost only)
DISCOVER_SWISS_MCP_TRANSPORT=streamable-http python -m discover_swiss_mcp
```

The key is read from the environment only. It is held as a secret value, is
never written to a log line, and belongs in no file that gets committed.

---

## Available Tools

<!-- Names exactly as registered — not the function names. -->

All eight tools are read-only (`readOnlyHint: true`, `openWorldHint: true`).
Every hit carries its own attribution; every response counts what it withheld
(`excluded_by_license`, `excluded_test_objects`, `excluded_by_default_types`)
and explains an empty result in `hint`.

| Tool | Source | Purpose |
|---|---|---|
| `search` | `POST /search` | Full text (`match: all\|name`), type, locality and distance (`near`, `radius_km`) across the whole index; rooms and meeting rooms excluded unless requested |
| `get_details` | `/vertices/{id}` | Description, fees, accessibility, opening hours, amenities — trimmed to ~8 KB, HTML resolved to text; `no_derivatives` for CC BY-ND |
| `find_accommodation` | Search `type=LodgingBusiness` | Stars, garni, price band, amenities, accessibility (Pro Infirmis / OK:GO), distance; no availability, no nightly prices |
| `find_tours` | Search `type=Tour` | Kind, difficulty, length, ascent, season month, region, distance |
| `find_events` | Search `type=Event`, OData schedule filter | Date range (default 30 days); thin coverage stated in the description; test objects and all-rights-reserved events withheld and counted; the 2099 sentinel is reported as `date_open`, never as a date |
| `webcams_near` | Search `type=Webcam` + `geo.distance` | Radius (default 25 km) or region; `live_url` for the live image, `snapshot_url` labelled as a stored still |
| `explore_area` | Search with facets | Counts by type, data owner, season, price band for a region, locality or radius; short facet names mapped to OData, dropped names reported in `missing_facets` |
| `source_status` | `/status`, counters, unfiltered facet count | Reachability, search availability, calls per minute, quota state, index size, coverage, entitlement state; works without a key |

Tool definitions are pinned in `docs/tool-hashes.json`; after an intended
change, run `python scripts/gen_tool_hashes.py --write` in the same PR.

---

## Attribution

Every response names its providers, and the host has to show them.

Each hit carries an `attribution` object — provider, licence and the
provider's own copyright notice (for example «Zürich Tourismus
www.zuerich.com», CC BY-SA). One result set can mix three licences: Zürich
Tourismus (CC BY-SA), SchweizMobil (CC BY), TOMAS (CC BY-ND). A single licence
line in a footer covers none of them correctly.

- **Hosts and assistants:** display provider and licence with the content
  taken from a hit. CC BY-SA content passed on stays CC BY-SA.
- **CC BY-ND** (`no_derivatives: true`, mostly TOMAS rooms): quote or state
  facts, never rewrite the description.
- **Withheld objects** (all rights reserved, no licence) are not served at all;
  `excluded_by_license` says how many there were.

The rules and the whitelist are in [docs/LICENSES.md](docs/LICENSES.md).

---

## Architecture decision

**ARCH A — live API only, search-centred, with a list fallback.**
(`probes/PROBE_REPORT_discover-swiss-mcp.md`, section 6)

- `/search` covers full text, type, place, distance, dates and facets in one
  endpoint. Seven of eight tools are views on it; `/vertices/{id}` serves the
  detail.
- There is no dump to mirror, and at 60 calls/minute and 50,000 a month a
  cache is enough: 15 minutes for search, 24 hours for detail. A monthly quota
  exhausted (`403` with «quota») is a state — `degraded: quota_exhausted` —
  and is never retried.
- **The risk is the entitlement.** Search contradicts the documentation and
  can be withdrawn. On `401`/`403` from `/search`, `search` and
  `find_accommodation` fall back to the typed list endpoints with client-side
  locality and distance filtering, answer `provenance: list_fallback`,
  `degraded: search_unavailable`, and say in `hint` what they ignored. The
  fallback is deliberately narrow: no full text, no star/price/amenity
  filters, at most eight list calls per tool call.
- One project only: `dsod-content`. `dsod-hs` is a subset.

---

## Known limitations

The twelve findings of the live probe that shape how this server behaves
(probe report, section 10; details in [CHANGELOG.md](CHANGELOG.md)):

1. **The documentation denies search; the API grants it.** Release gate: written confirmation.
2. **The documented example project `demo-web` answers 400.** Projects come from `/projects`.
3. **Paging is `nextPageToken`, not `continuation`.** Field names from live answers, not from the docs.
4. **`top=1000` does not mean 1000.** Cosmos DB cuts at ~4 MB; the token is followed.
5. **An open product is not an open licence.** All-rights-reserved and unlicensed objects are withheld and counted.
6. **`ds-containedInPlaceFilter` is not a filter.** It trims the response; the hit filter is the query parameter.
7. **Schweiz Tourismus already supplies data** (2,769 hotels) — the open channel carries their content.
8. **Unknown facet names are dropped silently.** Only verified names are sent; drops are reported in `missing_facets`.
9. **One hotel weighs 78 KB.** `get_details` trims to ~8 KB.
10. **There is test data in the production index.** «Demo Event» is withheld and counted in `excluded_test_objects`.
11. **Descriptions are HTML with entities.** Resolved to plain text server-side.
12. **Half the index is rooms and meeting rooms.** `search` excludes them unless asked.

---

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DISCOVER_SWISS_KEY` | yes | — | Subscription key, sent as `Ocp-Apim-Subscription-Key` |
| `DISCOVER_SWISS_PROJECT` | no | `dsod-content` | Project to query; `dsod-hs` is a subset |
| `DISCOVER_SWISS_MCP_TRANSPORT` | no | `stdio` | `stdio` or `streamable-http` |
| `DISCOVER_SWISS_MCP_HOST` | no | `127.0.0.1` | Bind address for HTTP transport |
| `DISCOVER_SWISS_MCP_PORT` | no | `8000` | TCP port for HTTP transport |
| `DISCOVER_SWISS_MCP_LOG_LEVEL` | no | `INFO` | structlog level; JSON goes to stderr |
| `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED` | no | `pending` | Date (`YYYY-MM-DD`) of discover.swiss's written search confirmation; reported by `source_status` |

---

## Project Structure

```
discover-swiss-mcp/
├── src/discover_swiss_mcp/
│   ├── __main__.py        # python -m entry point, transport chosen by env
│   ├── server.py          # MCP server, lifespan, tool wrappers
│   ├── tools.py           # the *_impl functions, input and output models
│   ├── config.py          # settings from env; the key is a SecretStr
│   ├── models.py          # the response envelope
│   ├── licenses.py        # licence whitelist, attribution, test-object filter
│   ├── transform.py       # HTML to text, detail trimming
│   ├── net.py             # SSRF guard, DNS pinning
│   ├── client.py          # API client: rate limit, retries, cache, list fallback
│   └── logging_config.py  # structlog, JSON to stderr
├── tests/                 # unit tests; test_live.py is the `live` marker, not run by CI
├── probes/                # live probe: scripts, raw responses, report
├── audits/                # audit reports (mcp-audit)
├── docs/                  # LICENSES.md, DEMO.md, tool-hashes.json
└── scripts/               # repo validation, release gate, tool hashes
```

---

## Testing

```bash
# What CI runs — no network
pytest -m "not live"
ruff check .
ruff format --check .
python scripts/validate_repo.py .

# Live canaries — real API, key from the environment, never in CI
export DISCOVER_SWISS_KEY="your-subscription-key"
pytest -m live -rA
```

The live canaries (`tests/test_live.py`, about twenty calls) hold each tool to
roughly half of what the index held on 2026-09-17 — «Landesmuseum» ≥ 20 hits,
hotels ≥ 2,000, webcams within 100 km of St. Gallen ≥ 30, and so on — and
check that scope parameters take effect: `match="name"` narrows,
`containedInPlace/id` comes back as a facet, the Landesmuseum description
arrives without HTML entities, the nearest hotel to Interlaken is in
Interlaken. A floor that fails means a tool stopped finding what is there.
Without a key the module skips; a skip is not a pass.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

---

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

Please report vulnerabilities as described in [SECURITY.md](SECURITY.md).

---

## License

MIT License — see [LICENSE](LICENSE)

The **software** is MIT. The **data** is not: it stays under the licence of the
provider named in each hit. See [docs/LICENSES.md](docs/LICENSES.md).

---

## Author

Hayal Oezkan · [malkreide](https://github.com/malkreide)

---

## Credits & Related Projects

- **Data:** [discover.swiss](https://discover.swiss/) Infocenter Open — data by the providers named per object
- **Protocol:** [Model Context Protocol](https://modelcontextprotocol.io/) — Anthropic / Linux Foundation
- **Conventions:** [openlex-mcp](https://github.com/malkreide/openlex-mcp) — reference implementation of this portfolio
- **Portfolio:** [Swiss Public Data MCP Portfolio](https://github.com/malkreide)
