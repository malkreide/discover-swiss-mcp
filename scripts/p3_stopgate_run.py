#!/usr/bin/env python3
"""STOP-GATE P3: `explore_area` for «Glarnerland» and `source_status`, live.

Runs both through the same ``*_impl`` functions the MCP wrappers call and
prints the envelope fields that decide whether they are right: the resolved
area, the total, every facet with its first values, `missing_facets`, and the
status counters. A third call asks for one invented facet name, to show that
the silent drop upstream reaches the response as `missing_facets`. Nothing is
written to disk.

The key comes from the environment and nowhere else:

    export DISCOVER_SWISS_KEY=...        # never in a committed file
    python scripts/p3_stopgate_run.py

Budget: about six calls against the monthly 50'000.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from discover_swiss_mcp.client import DiscoverSwissClient  # noqa: E402
from discover_swiss_mcp.config import ConfigError, load_settings  # noqa: E402
from discover_swiss_mcp.tools import (  # noqa: E402
    ExploreAreaInput,
    ExploreAreaResponse,
    explore_area_impl,
    source_status_impl,
)


def _explore_summary(label: str, response: ExploreAreaResponse) -> None:
    print(f"\n=== {label}")
    print(
        f"    provenance={response.provenance} degraded={response.degraded} total={response.total}"
    )
    if response.area is not None:
        print(f"    area={response.area.model_dump()}")
    print(f"    requested={response.requested_facets} missing={response.missing_facets}")
    for name, values in response.facets.items():
        shown = ", ".join(f"{v.label or v.value} ({v.value}) {v.count}" for v in values[:6])
        print(f"    {name}: {shown}")
    if response.hint:
        print(f"    hint={response.hint}")


async def main() -> int:
    try:
        settings = load_settings(require_key=True)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2

    client = DiscoverSwissClient(settings)
    try:
        glarus = await explore_area_impl(
            client,
            ExploreAreaInput(
                region="Glarnerland",
                facets=["leafType", "sourcePartner", "season", "priceRange", "containedInPlace"],
            ),
        )
        _explore_summary("explore_area: region Glarnerland", glarus)

        dropped = await explore_area_impl(
            client, ExploreAreaInput(region="Glarnerland", facets=["leafType", "difficultyX"])
        )
        _explore_summary("explore_area: one invented facet name", dropped)

        status = await source_status_impl(client)
        print("\n=== source_status")
        for field in (
            "api_key_configured",
            "reachable",
            "search_available",
            "project",
            "base_url",
            "calls_last_minute",
            "monthly_quota_exhausted_since",
            "last_success",
            "cache_entries",
            "index_total",
            "degraded",
            "hint",
            "coverage",
            "entitlement_note",
        ):
            print(f"    {field}={getattr(status, field)}")
    finally:
        await client.aclose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
