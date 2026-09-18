"""Entry point for ``python -m discover_swiss_mcp``.

Transport selection lives in :func:`discover_swiss_mcp.server.main` and is
driven by ``DISCOVER_SWISS_MCP_TRANSPORT`` — the same code path the console
script uses, so both entry points behave identically.
"""

from discover_swiss_mcp.server import main

main()
