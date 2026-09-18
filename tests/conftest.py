"""Shared test fixtures.

Unit tests run offline. The respx fixture below is the seam every future API
test mounts on: the live API is reached only from tests marked ``live``, which
CI does not run.
"""

from __future__ import annotations

import os

import pytest
import respx

from discover_swiss_mcp.config import API_BASE_URL

TEST_KEY = "test-key"


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


@pytest.fixture
def api_mock():
    """A respx router bound to the Infocenter base URL.

    ``assert_all_called=False`` so a test may register more routes than it
    exercises; what matters is that nothing unrouted escapes, and respx raises
    on an unmatched request by itself.
    """
    with respx.mock(base_url=API_BASE_URL, assert_all_called=False) as router:
        yield router
