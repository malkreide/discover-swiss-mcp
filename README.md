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

**pre-release — search entitlement confirmation from discover.swiss pending.**

The live probe of 2026-09-17 found that `/search` works for the Open
subscription — full text, distance ranking, date filters, 31 facets — although
the official documentation states the opposite ("You can't use the search
functionality"). The whole server is built on that endpoint, which makes the
contradiction its main risk: an entitlement that contradicts the docs can be
withdrawn without notice.

Two consequences, both already decided:

- Written confirmation from discover.swiss is a **release gate**. No release
  before that conversation has happened.
- The server carries a fallback. On `401`/`403` from `/search`, `search` and
  `find_accommodation` fall back to the typed list endpoints with client-side
  locality and distance filtering, and label the answer
  `provenance: list_fallback`, `degraded: search_unavailable`. The fallback is
  deliberately narrow — no full text, no star/price/amenity filters, at most
  eight list calls per tool call, and an incomplete scan says so in `hint`.
- `source_status` reports the state of that confirmation, read from
  `DISCOVER_SWISS_ENTITLEMENT_CONFIRMED` (`pending` until set).

Status: **P3** — all eight tools are registered.

---

## Overview

`discover-swiss-mcp` gives AI assistants access to the open index of
[discover.swiss](https://discover.swiss/) — 20,817 objects of Swiss tourism
data in schema.org shape, licence and attribution attached to every single
object.

Coverage is uneven, and knowing where is part of using it well:

| Domain | Coverage | Detail |
|---|---|---|
| Accommodation | **nationwide** | 5,275 businesses, 10,112 rooms — Zermatt to Geneva |
| Points of interest | **regional** | Zurich (1,311), Eastern Switzerland partners, Liechtenstein, Engadin Scuol |
| Tours, webcams, ski resorts | regional | 223 tours, 73 webcams, 21 ski resorts |
| Events | **near-empty** | 21 entries, test objects among them |

There is no POI content for the Bernese Oberland, Central Switzerland, Valais,
Ticino or the Romandie. A tool that hides that produces a confident answer
about a region it has no data for.

**Anchor demo query:** *"I have a rainy day in Zurich — which museums are
within walking distance of the main station, and where do I eat vegetarian
afterwards?"*

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

The eight tools of the probe report, section 7. All are read-only
(`readOnlyHint: true`, `openWorldHint: true`). Every hit carries its own
attribution; every response counts what it withheld (`excluded_by_license`,
`excluded_test_objects`, `excluded_by_default_types`) and explains an empty
result in `hint`.

| Tool | Status | Source | Purpose |
|---|---|---|---|
| `search` | available | `POST /search` | Full text (`match: all\|name`), type, locality and distance (`near`, `radius_km`) across the whole index; rooms and meeting rooms excluded unless requested |
| `get_details` | available | `/vertices/{id}` | Description, fees, accessibility, opening hours, amenities — trimmed to ~8 KB, HTML resolved to text; `no_derivatives` for CC BY-ND |
| `find_accommodation` | available | Search `type=LodgingBusiness` | Stars, garni, price band, amenities, accessibility (Pro Infirmis / OK:GO), distance; no availability, no nightly prices |
| `find_tours` | available | Search `type=Tour` | Kind, difficulty, length, ascent, season month, region, distance |
| `find_events` | available | Search `type=Event`, OData schedule filter | Date range (default 30 days); thin coverage stated in the description; test objects and all-rights-reserved events withheld and counted; the 2099 sentinel is reported as `date_open`, never as a date |
| `webcams_near` | available | Search `type=Webcam` + `geo.distance` | Radius (default 25 km) or region; `live_url` for the live image, `snapshot_url` labelled as a stored still |
| `explore_area` | available | Search with facets | Counts by type, data owner, season, price band for a region, locality or radius; short facet names mapped to OData, dropped names reported in `missing_facets` |
| `source_status` | available | `/status`, counters, unfiltered facet count | Reachability, search availability, calls per minute, quota state, index size, coverage, entitlement state; works without a key |

Tool definitions are pinned in `docs/tool-hashes.json`; after an intended
change, run `python scripts/gen_tool_hashes.py --write` in the same PR.

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

Data licences and the attribution rules are documented in
[docs/LICENSES.md](docs/LICENSES.md).

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
│   ├── client.py          # API client: rate limit, retries, cache, list fallback
│   └── logging_config.py  # structlog, JSON to stderr
├── tests/                 # unit tests; `live` marker is not run by CI
├── probes/                # live probe: scripts, raw responses, report
├── docs/LICENSES.md       # licence whitelist and attribution rules
└── scripts/               # repo validation and release gate
```

---

## Testing

```bash
# What CI runs — no network
pytest -m "not live"

ruff check .
ruff format --check .
```

Unit tests run offline. Tests marked `live` hit the real API and need a
subscription key; CI never runs them.

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
