"""HTTP client for the discover.swiss Infocenter V2 API — P0 stub.

Nothing here talks to the network yet. P0 is scaffold only; the TODO markers
below record what the live probe of 2026-09-17 established, so P1 implements
the measured behaviour rather than the documented one. Where the two disagree,
``probes/PROBE_REPORT_discover-swiss-mcp.md`` is authoritative — the docs are
demonstrably wrong about search entitlement, the paging field names and the
example project.
"""

from __future__ import annotations

from typing import Any

from discover_swiss_mcp import __version__
from discover_swiss_mcp.config import Settings
from discover_swiss_mcp.logging_config import get_logger

logger = get_logger("discover_swiss_mcp.client")

USER_AGENT = f"discover-swiss-mcp/{__version__} (+https://github.com/malkreide/discover-swiss-mcp)"

# Search select whitelist: `IndexResponse` minus `containedInPlace` and
# `context` (46 of 48 fields). Sending all 48 answers 400, so the list is
# hard-coded rather than derived — verified field by field in probe run 3.
# TODO(P1): fill from probes/probe_verify_out/ and cover with a test.
SEARCH_SELECT_FIELDS: tuple[str, ...] = ()


class DiscoverSwissClient:
    """Thin async wrapper around the Infocenter V2 endpoints.

    One shared client per server process, created in the server lifespan and
    closed on shutdown — not one per tool call.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def settings(self) -> Settings:
        return self._settings

    def request_headers(self, lang: str = "de") -> dict[str, str]:
        """Headers for one outbound request.

        ``Accept-Language`` is always explicit: the API defaults to de-CH and
        silently returns German names otherwise.
        """
        return {
            **self._settings.auth_header,
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": lang,
        }

    # -- P1 ----------------------------------------------------------------
    #
    # TODO(P1): `search(...)` — POST /search. `project` is mandatory and goes in
    #   as an array (401 without it). `resultsPerPage` up to 1000 works; paging
    #   runs over `currentPage`. The response envelope is
    #   `{count, values[], facets{}}`.
    # TODO(P1): `get_vertex(id)` — GET /vertices/{id}. Responses reach 78 KB per
    #   hotel, so the caller truncates: 3 photos, amenities as names only,
    #   dataGovernance down to provider plus licence.
    # TODO(P1): list-endpoint fallback — GET /{collection} with an explicit
    #   `top`, `select` and `project`, following `nextPageToken` (NOT
    #   `continuation`, and `hasNextPage` is a bool, not a token). `top=1000`
    #   does not mean 1000: Cosmos cuts at roughly 4 MB.
    # TODO(P1): retry policy — 3 attempts at 2s/4s/8s for 5xx and network
    #   errors; never for 4xx except 429, which waits the number of seconds
    #   named in the message. A 403 carrying "quota" is not retried at all; it
    #   is the state `degraded: quota_exhausted`.
    # TODO(P1): SSRF hardening with DNS pinning, following `openlex-mcp/net.py`.
    # TODO(P1): licence whitelist on the root `license` field
    #   {CC0, CC BY, CC BY-SA, CC BY-ND, ODbL}; everything else is counted into
    #   `excluded_by_license` and never served.
    # TODO(P1): HTML descriptions are HTML with entities — strip tags and
    #   resolve entities server-side, with the Landesmuseum description as the
    #   fixture.

    async def aclose(self) -> None:
        """Close the shared transport. No-op while the client is a stub."""
        return None

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        # Goes through `safe_summary()` so the key cannot leak into a traceback.
        summary: dict[str, Any] = dict(self._settings.safe_summary())
        return f"DiscoverSwissClient({summary})"
