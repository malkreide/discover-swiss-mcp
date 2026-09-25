#!/usr/bin/env python3
"""Probe: which rule recovers a search hit's licence?

`/search` returns neither a root `license` nor `dataGovernance.provider`, so
the licence of a hit has to be read from `dataGovernance.origin`. This probe
fetches three hits each of five types, loads the detail object of every hit
(`/vertices/{id}`, whose root `license` is authoritative) and compares two
candidate rules against it:

* `datasource` — the origins whose datasource is listed in the hit's own
  `datasource` field,
* `first` — the licence of the first origin.

About 20 calls. The key comes from the environment only:

    DISCOVER_SWISS_KEY=... python probes/probe_license.py

First run: 2026-09-25, result in `PROBE_LICENSE_discover-swiss.md`.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from discover_swiss_mcp.client import DiscoverSwissClient  # noqa: E402
from discover_swiss_mcp.config import load_settings  # noqa: E402
from discover_swiss_mcp.tools import TOOL_SELECT  # noqa: E402

SAMPLES = [
    ("Museum", {"leafType": ["Museum"], "addressLocality": ["Zürich"]}),
    ("Hotel", {"leafType": ["Hotel"], "addressLocality": ["Interlaken"]}),
    ("Tour", {"type": ["Tour"]}),
    ("Webcam", {"leafType": ["Webcam"]}),
    ("HotelRoom", {"leafType": ["HotelRoom"]}),
]


def origins(hit):
    governance = hit.get("dataGovernance") or {}
    return [o for o in governance.get("origin") or [] if isinstance(o, dict)]


async def main() -> None:
    client = DiscoverSwissClient(load_settings())
    agree = {"datasource": 0, "first": 0}
    n = 0
    try:
        for label, body in SAMPLES:
            result = await client.search(
                {**body, "resultsPerPage": 3, "select": TOOL_SELECT + ",datasource"}
            )
            for hit in result.values:
                ident = hit.get("identifier")
                detail = await client.get_vertex(ident) or {}
                root = detail.get("license")
                owner = ((detail.get("dataGovernance") or {}).get("provider") or {}).get("acronym")
                datasources = hit.get("datasource") or []
                og = origins(hit)
                by_ds = [o.get("license") for o in og if o.get("datasource") in datasources]
                first = og[0].get("license") if og else None
                n += 1
                agree["datasource"] += int(len(set(by_ds)) == 1 and by_ds[0] == root)
                agree["first"] += int(first == root)
                print(f"{label:9} {ident}")
                print(f"    root={root} owner={owner} hit.datasource={datasources}")
                print(f"    rule datasource={by_ds} | rule first={first}")
                print(
                    "    origins: "
                    + ", ".join(
                        f"{o.get('datasource')}:{o.get('license')}:"
                        f"{(o.get('provider') or {}).get('acronym')}"
                        for o in og
                    )
                )
        print(f"\nAGREEMENT with root licence over {n} hits: {agree}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
