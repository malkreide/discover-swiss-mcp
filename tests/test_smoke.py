"""Smoke tests: the server imports, and it exposes exactly the eight tools.

The tool-list assertion is the point. The eight names are the full set of the
probe report, and an assertion on them means a ninth tool appears only in a
commit that had to change this file — rather than sliding in unnoticed.
"""

from __future__ import annotations

import pytest

from discover_swiss_mcp import __version__
from discover_swiss_mcp.client import DiscoverSwissClient
from discover_swiss_mcp.config import DEFAULT_PROJECT, ConfigError, load_settings
from discover_swiss_mcp.server import MCP_PROTOCOL_VERSION, app_lifespan, mcp


def test_package_imports_with_a_version() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_server_object_is_built() -> None:
    assert mcp.name == "discover_swiss_mcp"
    assert MCP_PROTOCOL_VERSION.count("-") == 2


TOOLS = {
    "search",
    "get_details",
    "find_accommodation",
    "find_tours",
    "find_events",
    "webcams_near",
    "explore_area",
    "source_status",
}


async def test_tool_list_is_the_full_set() -> None:
    """Eight tools, and no more than the portfolio's ceiling of fifteen."""
    names = {tool.name for tool in await mcp.list_tools()}
    assert names == TOOLS
    assert len(names) <= 15


def test_settings_come_from_the_environment(api_key) -> None:
    settings = load_settings()
    assert settings.api_key.get_secret_value() == api_key
    assert settings.project == DEFAULT_PROJECT
    assert settings.transport == "stdio"


def test_missing_key_is_a_named_error(monkeypatch) -> None:
    monkeypatch.delenv("DISCOVER_SWISS_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_settings()


def test_key_is_not_in_any_printable_form() -> None:
    """The secret must survive repr, str, dumps and the log summary."""
    settings = load_settings()
    client = DiscoverSwissClient(settings)
    for rendered in (repr(settings), str(settings), settings.model_dump_json(), repr(client)):
        assert "test-key" not in rendered
    assert settings.safe_summary()["api_key"] == "set"
    # The one place that unwraps it is the outbound header.
    assert settings.auth_header["Ocp-Apim-Subscription-Key"] == "test-key"


async def test_lifespan_logs_its_start_without_the_key() -> None:
    """The lifespan runs, says so, and says nothing about the key's value."""
    import structlog

    with structlog.testing.capture_logs() as events:
        async with app_lifespan(mcp) as ctx:
            assert ctx.settings is not None
            assert ctx.settings.project == DEFAULT_PROJECT

    rendered = [e for e in events if e.get("event") == "Server lifespan started"]
    assert len(rendered) == 1
    assert rendered[0]["tools"] == len(TOOLS)
    assert rendered[0]["api_key"] == "set"
    assert "test-key" not in str(events)


async def test_lifespan_hands_out_one_shared_client() -> None:
    """The rate budget and the cache only work if every call shares one client."""
    async with app_lifespan(mcp) as ctx:
        assert ctx.client is not None
        assert ctx.client.settings is ctx.settings


def test_windows_install_carries_the_time_zone_database() -> None:
    """Windows has no IANA database; `zoneinfo` needs `tzdata` there.

    CI runs on Linux only and cannot see the failure itself, so the
    declaration is held here.
    """
    import tomllib
    from pathlib import Path

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    dependencies = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["dependencies"]
    assert any(d.replace(" ", "").startswith("tzdata;sys_platform=='win32'") for d in dependencies)
