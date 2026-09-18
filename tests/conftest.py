"""Shared test fixtures.

Unit tests run offline. Two seams make that work:

* :func:`api_mock` — a respx router bound to the **pinned** base URL. The
  client resolves the host once and connects to the IP (``net._resolve`` is
  patched to a documentation address), so the URL respx has to match is the
  pinned one, not the public one. Mocking the public URL would look right and
  match nothing.
* :func:`sleeps` — replaces ``client._sleep``, the module alias, so waiting
  costs no wall-clock time and the delays can be asserted. Patching
  ``asyncio.sleep`` itself would silence every sleep in the process.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from discover_swiss_mcp import client as client_module
from discover_swiss_mcp import net
from discover_swiss_mcp.client import DiscoverSwissClient
from discover_swiss_mcp.config import API_BASE_URL, load_settings

TEST_KEY = "test-key"

# TEST-NET-3 (RFC 5737). A documentation address can never be a real host, and
# it is outside every range `net.BLOCKED_NETWORKS` refuses.
PINNED_IP = "203.0.113.10"
PINNED_BASE = net._pin_url(API_BASE_URL, PINNED_IP)

PROBE_DIR = Path(__file__).resolve().parent.parent / "probes"


@pytest.fixture(autouse=True)
def api_key(monkeypatch) -> str:
    """Put a deterministic subscription key in the environment.

    Autouse on purpose: a test that forgets to set it would otherwise pick up
    a real key from the developer's shell and quietly hit the live API.
    """
    monkeypatch.setenv("DISCOVER_SWISS_KEY", TEST_KEY)
    return TEST_KEY


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch) -> None:
    """Remove the remaining DISCOVER_SWISS_* variables.

    Without this, a developer running with ``DISCOVER_SWISS_PROJECT=dsod-hs``
    exported gets different test results than CI — the kind of difference that
    shows up as "works on my machine" three commits later.
    """
    for name in os.environ:
        if name.startswith("DISCOVER_SWISS_") and name != "DISCOVER_SWISS_KEY":
            monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _pin_dns(monkeypatch) -> None:
    """Resolve every host to the documentation address, without a lookup."""

    async def _resolve(_host: str, _port: int) -> list[str]:
        return [PINNED_IP]

    monkeypatch.setattr(net, "_resolve", _resolve)


@pytest.fixture
def sleeps(monkeypatch) -> list[float]:
    """Record every wait and return immediately. The list is the assertion."""
    recorded: list[float] = []

    async def _fake_sleep(seconds: float) -> None:
        recorded.append(seconds)

    monkeypatch.setattr(client_module, "_sleep", _fake_sleep)
    return recorded


@pytest.fixture
def api_mock():
    """A respx router bound to the pinned Infocenter base URL.

    ``assert_all_called=False`` so a test may register more routes than it
    exercises; what matters is that nothing unrouted escapes, and respx raises
    on an unmatched request by itself.
    """
    with respx.mock(base_url=PINNED_BASE, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def client():
    """A client on its own transport, closed after the test."""
    instance = DiscoverSwissClient(load_settings())
    try:
        yield instance
    finally:
        await instance.aclose()


def probe_fixture(*parts: str) -> Any:
    """Load a recorded probe response. The probes are the reference, not a mock."""
    return json.loads(PROBE_DIR.joinpath(*parts).read_text(encoding="utf-8"))


def json_response(payload: Any, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=payload)
