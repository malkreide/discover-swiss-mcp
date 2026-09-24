"""Response envelope shared by every tool.

Two rules this file exists to enforce:

1. **Attribution travels with the data, not with the README.** Every object in
   the open index carries its own ``copyrightNotice``, provider and licence,
   and they differ per hit — Zurich Tourismus (CC BY-SA), SchweizMobil (CC BY),
   TOMAS (CC BY-ND) can all appear in one result set. A licence note in the
   README covers none of them.

2. **What the model does not see, it must be told about.** ``degraded``,
   ``hint``, ``excluded_by_license`` and ``excluded_test_objects`` exist so an
   empty or shortened result is legible as such. An empty list with no
   explanation is the shape that invites an invented answer.

:class:`Attribution` itself lives in :mod:`discover_swiss_mcp.licenses`, next to
the rules that build it, and is re-exported here so the tool layer has one
import for the response shape.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from discover_swiss_mcp.licenses import Attribution

__all__ = ["Attribution", "Envelope"]


class Envelope(BaseModel):
    """Common envelope around every tool response."""

    source: str = (
        "discover.swiss Infocenter Open — data by the providers named per hit; see attribution[]"
    )
    provenance: Literal["live_api", "cached", "list_fallback"]
    retrieved_at: datetime
    source_freshness: str | None  # lastModified of the most recent hit, else None
    project: str
    # None | "quota_exhausted" | "upstream_unreachable" | "search_unavailable"
    degraded: str | None = None
    disclaimer: str | None = None
    hint: str | None = None
    excluded_by_license: int = 0
    excluded_test_objects: int = 0
    # Rooms and meeting rooms dropped because the caller did not ask for them.
    # Almost half the index is one or the other (9'838 of 20'817, probe 5.2);
    # left in, 61 double rooms of one hotel push every museum off the page.
    # Counted rather than hidden, like the two counters above.
    excluded_by_default_types: int = 0
