#!/usr/bin/env python3
"""Probe: which filters separate the tour kinds?

Two runs on 2026-09-25, recorded in `PROBE_TOURKINDS_discover-swiss.md`:

1. the facets `leafType`, `categoryTree` and `tag` over `type=Tour`
   (1 call) — which values exist at all,
2. ten filter combinations (10 calls) — whether `categoryTree` wants the full
   path or the short code, and whether `leafType` and `categoryTree` are ANDed.

The key comes from the environment only:

    DISCOVER_SWISS_KEY=... python probes/probe_tour_kinds.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from discover_swiss_mcp.client import DiscoverSwissClient  # noqa: E402
from discover_swiss_mcp.config import load_settings  # noqa: E402

FACETS = ["leafType", "categoryTree", "tag"]

HIKE = ["HikingTrail", "Route", "Way", "Tour", "Longdistance", "NatureTrail", "ThemeTrail"]
WINTER_LEAF = ["CrossCountry", "TobogganRun", "SkiSlope"]
CASES = [
    ("A  hiking leafTypes", {"leafType": HIKE}),
    ("B  winter cat, full path", {"categoryTree": ["sui_root|sui_01|sui_0110"]}),
    ("C  winter cat, short", {"categoryTree": ["sui_0110"]}),
    ("D  cycling cat, full path", {"categoryTree": ["sui_root|sui_01|sui_0102"]}),
    ("E  mtb cat, full path", {"categoryTree": ["sui_root|sui_01|sui_0102|sui_010205"]}),
    ("F  foot cat, full path", {"categoryTree": ["sui_root|sui_01|sui_0101"]}),
    ("G  winter leafTypes", {"leafType": WINTER_LEAF}),
    (
        "H  hiking leaf AND winter cat",
        {"leafType": HIKE, "categoryTree": ["sui_root|sui_01|sui_0110"]},
    ),
    ("I  hiking leaf + season jul", {"leafType": HIKE, "season": ["jul"]}),
    ("J  BikeTrail leafType", {"leafType": ["BikeTrail"]}),
]


async def main() -> None:
    client = DiscoverSwissClient(load_settings())
    try:
        result = await client.search(
            {
                "type": ["Tour"],
                "resultsPerPage": 1,
                "select": "identifier",
                "facets": [{"name": f, "count": 60} for f in FACETS],
            }
        )
        print("Tours total:", result.count, "| missing facets:", result.missing_facets)
        for facet in FACETS:
            print(f"\n== {facet}")
            for value in (result.facets.get(facet) or {}).get("values", []):
                print(f"   {value.get('count'):>4}  {value.get('value')}  ({value.get('name')})")

        print()
        for label, body in CASES:
            result = await client.search(
                {
                    "type": ["Tour"],
                    **body,
                    "resultsPerPage": 3,
                    "select": "identifier,name,additionalType",
                }
            )
            names = ", ".join(f"{v.get('name')} [{v.get('additionalType')}]" for v in result.values)
            print(f"{label:32} count={result.count:>4}  {names[:150]}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
