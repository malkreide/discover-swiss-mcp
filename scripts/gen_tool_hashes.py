#!/usr/bin/env python3
"""Hash snapshot of the tool definitions (SEC-022, rug-pull protection).

Builds one SHA-256 per tool over its *contract* — name, description, input and
output schema — and compares it with the committed snapshot
`docs/tool-hashes.json`. A difference means the observable definition of a
tool has changed. CI then fails, so that a silent change of what a tool claims
to do does not ship unnoticed.

An intended change is confirmed by rewriting the snapshot in the same PR
(`--write`), which puts it in the review diff.

Usage:
    python scripts/gen_tool_hashes.py --check    # CI: fail on any difference
    python scripts/gen_tool_hashes.py --write    # after an intended change
    python scripts/gen_tool_hashes.py --print    # print only

The pattern is the one `openlex-mcp` runs, including its two lessons: the hash
reads the public `mcp.list_tools()` with the wire names `inputSchema` /
`outputSchema`, not SDK internals; and the description is normalised with
`inspect.cleandoc`, because Python 3.13 dedents docstrings at compile time and
3.11 does not — a raw hash would be red on one leg of the CI matrix forever.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import sys
from pathlib import Path

# Runs from the repository root without an installation.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

SNAPSHOT = Path(__file__).resolve().parent.parent / "docs" / "tool-hashes.json"


def _tool_hash(tool) -> str:
    """Stable SHA-256 over the observable contract of one tool."""
    payload = {
        "name": tool.name,
        "description": inspect.cleandoc(tool.description or ""),
        "inputSchema": tool.input_schema,
        "outputSchema": getattr(tool, "output_schema", None),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


async def current_hashes() -> dict[str, str]:
    from discover_swiss_mcp.server import mcp

    tools = await mcp.list_tools()
    return {t.name: _tool_hash(t) for t in sorted(tools, key=lambda t: t.name)}


def current_snapshot(hashes: dict[str, str]) -> dict:
    from discover_swiss_mcp import server as srv

    return {
        "mcp_protocol_version": srv.MCP_PROTOCOL_VERSION,
        "tool_count": len(hashes),
        "tools": hashes,
    }


def load_snapshot() -> dict:
    if not SNAPSHOT.exists():
        return {}
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="SEC-022 tool hash snapshot")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="fail on any difference (default)")
    g.add_argument("--write", action="store_true", help="rewrite the snapshot")
    g.add_argument("--print", action="store_true", help="print the current hashes")
    args = ap.parse_args()

    hashes = asyncio.run(current_hashes())
    new = current_snapshot(hashes)

    if args.print:
        print(json.dumps(new, indent=2, ensure_ascii=False))
        return 0

    if args.write:
        SNAPSHOT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{SNAPSHOT.relative_to(SNAPSHOT.parents[1])} written: {len(hashes)} tools")
        return 0

    old = load_snapshot()
    if not old:
        print(f"No snapshot at {SNAPSHOT}. Create it with --write.", file=sys.stderr)
        return 1

    errors: list[str] = []
    if old.get("mcp_protocol_version") != new["mcp_protocol_version"]:
        errors.append(
            f"protocol version: snapshot {old.get('mcp_protocol_version')!r}, "
            f"server {new['mcp_protocol_version']!r}"
        )
    a, n = old.get("tools", {}), new["tools"]
    for name in sorted(set(a) - set(n)):
        errors.append(f"removed: {name}")
    for name in sorted(set(n) - set(a)):
        errors.append(f"added: {name}")
    for name in sorted(set(a) & set(n)):
        if a[name] != n[name]:
            errors.append(f"definition changed: {name}")

    if errors:
        print("Tool hashes differ from the snapshot (SEC-022):", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nIf the change was intended, rewrite in the same PR:\n"
            "    python scripts/gen_tool_hashes.py --write",
            file=sys.stderr,
        )
        return 1

    print(f"Tool hashes unchanged: {len(n)} tools, protocol {new['mcp_protocol_version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
