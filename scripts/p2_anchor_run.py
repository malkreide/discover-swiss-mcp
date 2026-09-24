#!/usr/bin/env python3
"""STOP-GATE P2: the three anchor queries of the probe report, section 8, live.

Runs every P2 tool at least once against the real API through the same
``*_impl`` functions the MCP wrappers call, and prints a compact summary per
call — counts, the excluded counters, the hint and the first hits with their
attribution. Nothing is written to disk.

The key comes from the environment and nowhere else:

    export DISCOVER_SWISS_KEY=...        # never in a committed file
    python scripts/p2_anchor_run.py

Budget: about ten calls against the monthly 50'000.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from discover_swiss_mcp.client import DiscoverSwissClient  # noqa: E402
from discover_swiss_mcp.config import ConfigError, load_settings  # noqa: E402
from discover_swiss_mcp.tools import (  # noqa: E402
    FindAccommodationInput,
    FindToursInput,
    GeoPoint,
    GetDetailsInput,
    SearchInput,
    find_accommodation_impl,
    find_tours_impl,
    get_details_impl,
    search_impl,
)

ZURICH_HB = GeoPoint(lat=47.3779, lon=8.5403)
BRAUNWALD = GeoPoint(lat=46.9404, lon=8.9995)
INTERLAKEN = GeoPoint(lat=46.6863, lon=7.8632)


def _summary(label: str, response: Any, extra: tuple[str, ...] = ()) -> None:
    print(f"\n=== {label}")
    print(
        f"    provenance={response.provenance} degraded={response.degraded} "
        f"upstream_count={getattr(response, 'upstream_count', None)} "
        f"fetched={getattr(response, 'fetched', None)} returned={getattr(response, 'returned', None)}"
    )
    print(
        f"    excluded: licence={response.excluded_by_license} "
        f"test={response.excluded_test_objects} default_types={response.excluded_by_default_types}"
    )
    if getattr(response, "area", None) is not None:
        print(f"    area={response.area.model_dump()}")
    if response.hint:
        print(f"    hint={response.hint}")
    if response.disclaimer:
        print(f"    disclaimer={response.disclaimer}")
    for hit in getattr(response, "hits", [])[:5]:
        fields = " ".join(f"{name}={getattr(hit, name)}" for name in extra)
        print(
            f"    - {hit.identifier} | {hit.name} | {hit.leaf_type} | {hit.locality} | "
            f"{hit.distance_km} km | {hit.attribution.provider} / {hit.attribution.license} {fields}"
        )


async def main() -> int:
    try:
        settings = load_settings(require_key=True)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2

    client = DiscoverSwissClient(settings)
    try:
        # Anchor 1 — rainy day in Zurich: museums near HB, vegetarian food after.
        museums = await search_impl(
            client, SearchInput(types=["Museum"], near=ZURICH_HB, radius_km=1.5)
        )
        _summary("A1 search: museums ≤ 1.5 km from Zurich HB", museums)
        veggie = await search_impl(
            client, SearchInput(query="vegetarisch", types=["Restaurant"], near=ZURICH_HB)
        )
        _summary("A1 search: 'vegetarisch' restaurants near HB", veggie)
        if museums.hits:
            detail = await get_details_impl(
                client, GetDetailsInput(identifier=museums.hits[0].identifier)
            )
            print(f"\n=== A1 get_details: {detail.identifier}")
            print(
                f"    name={detail.name} licence={detail.license} "
                f"no_derivatives={detail.no_derivatives} removed={detail.removed}"
            )
            print(f"    disclaimer={detail.disclaimer}")
            print(f"    detail keys={sorted((detail.detail or {}).keys())}")

        # Anchor 2 — Braunwald: tours with little ascent, webcams nearby.
        tours = await find_tours_impl(
            client, FindToursInput(near=BRAUNWALD, radius_km=10, ascent_m_max=300)
        )
        _summary(
            "A2 find_tours: ≤ 300 m ascent, ≤ 10 km from Braunwald",
            tours,
            ("length_km", "ascent_m", "difficulty", "duration_min"),
        )
        region = await find_tours_impl(client, FindToursInput(region="Glarnerland", kind="hiking"))
        _summary("A2 find_tours: region Glarnerland, hiking", region, ("length_km", "ascent_m"))
        webcams = await search_impl(
            client, SearchInput(types=["Webcam"], near=BRAUNWALD, radius_km=15)
        )
        _summary("A2 search: webcams ≤ 15 km from Braunwald", webcams)

        # Anchor 3 — family-friendly, three stars, accessible, near Interlaken.
        lodging = await find_accommodation_impl(
            client,
            FindAccommodationInput(near=INTERLAKEN, radius_km=5, stars_min=3, accessible=True),
        )
        _summary(
            "A3 find_accommodation: ≥ 3 stars, accessible, ≤ 5 km from Interlaken",
            lodging,
            ("stars", "garni", "accessibility_sources"),
        )
        if lodging.hits:
            detail = await get_details_impl(
                client, GetDetailsInput(identifier=lodging.hits[0].identifier, lang="en")
            )
            profiles = [
                a.get("ratingProfileName") for a in (detail.detail or {}).get("accessibility", [])
            ]
            print(f"\n=== A3 get_details (en): {detail.identifier} {detail.name}")
            print(f"    accessibility profiles={profiles}")
            print(f"    disclaimer={detail.disclaimer}")
    finally:
        await client.aclose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
