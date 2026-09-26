#!/usr/bin/env python3
"""Probe: what does `searchText` understand? (audit FID-005)

The spec says only «search for contained string by the searchable fields» — no
query language, no operators. The tool description therefore tells the model
to send plain words and calls everything else untested. This probe measures
the untested part, so the description can state facts instead of caution.

Each case runs twice: `searchFields` omitted (all fields, the tool's default
`match='all'`) and `searchFields=name`. Reading the table:

* prefix / fragment ≈ whole word  → prefixes match (the index stems or n-grams)
* wildcard ≈ whole word          → `*` is an operator; ≈ 0 → it is literal or dropped
* quoted phrase < both words     → phrases are understood
* AND < OR ≈ plain pair          → boolean operators are understood
* an error (HTTP 400)            → the syntax is rejected — never send it

The key comes from the environment only, about 26 calls:

    DISCOVER_SWISS_KEY=... python probes/probe_query_syntax.py

Results go to `probes/probe_query_out/results.json`; record the reading in a
`PROBE_QUERY_discover-swiss.md` next to it and update the `search` description.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from discover_swiss_mcp.client import DiscoverSwissClient, DiscoverSwissError  # noqa: E402
from discover_swiss_mcp.config import load_settings  # noqa: E402

OUT = Path(__file__).resolve().parent / "probe_query_out"

CASES = [
    ("whole word (reference)", "Landesmuseum"),
    ("prefix", "Landesmus"),
    ("fragment inside a compound", "museum"),
    ("wildcard *", "Landesmus*"),
    ("wildcard ?", "Landesmuse?m"),
    ("fuzzy ~", "Landesmusem~"),
    ("two words", "Landesmuseum Zürich"),
    ("quoted phrase", '"Landesmuseum Zürich"'),
    ("AND", "Landesmuseum AND Zürich"),
    ("OR", "Landesmuseum OR Kunsthaus"),
    ("minus", "Landesmuseum -Shop"),
    ("umlaut folded", "Zurich"),
    ("lower case", "landesmuseum"),
]


async def count(client: DiscoverSwissClient, text: str, name_only: bool) -> int | str:
    body = {"searchText": text, "resultsPerPage": 1, "select": "identifier"}
    if name_only:
        body["searchFields"] = "name"
    try:
        result = await client.search(body)
    except DiscoverSwissError as exc:
        return f"error: {type(exc).__name__}: {exc}"
    return result.count if result.count is not None else "no count"


async def main() -> None:
    client = DiscoverSwissClient(load_settings())
    rows = []
    try:
        for label, text in CASES:
            all_fields = await count(client, text, name_only=False)
            name_only = await count(client, text, name_only=True)
            rows.append({"case": label, "searchText": text, "all": all_fields, "name": name_only})
            print(f"{label:28} {text!r:32} all={all_fields!s:>8}  name={name_only!s:>8}")
    finally:
        await client.aclose()
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(
        json.dumps(
            {"run_at": datetime.now(UTC).isoformat(), "rows": rows}, ensure_ascii=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nwritten: {OUT / 'results.json'}")


if __name__ == "__main__":
    asyncio.run(main())
