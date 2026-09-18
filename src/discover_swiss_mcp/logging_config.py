"""Structured logging with structlog (OBS-003 / OBS-004).

JSON to **stderr**: stdout is reserved for the JSON-RPC stream, so a single
stray ``print`` on stdout corrupts the protocol. Severity levels are
RFC-5424-compatible, and :func:`tool_logger` binds the tool name plus a fresh
correlation id per call.

The subscription key never reaches a log record. It is held as a
``pydantic.SecretStr`` in :mod:`discover_swiss_mcp.config` and is never passed
to a logging call; see the note there.
"""

from __future__ import annotations

import logging
import sys
import uuid

import structlog

_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog with a JSON renderer writing to stderr.

    Idempotent — calling it again (tests plus ``main()``) is harmless and
    updates the log level.
    """
    global _configured

    logging.basicConfig(stream=sys.stderr, level=level.upper(), format="%(message)s")

    resolved = logging.getLevelName(level.upper())
    if not isinstance(resolved, int):
        resolved = logging.INFO

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(resolved),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        # Caching off so `structlog.testing.capture_logs()` works in tests and
        # so a re-configured level takes effect immediately.
        cache_logger_on_first_use=False,
    )
    _configured = True


def get_logger(name: str = "discover_swiss_mcp"):
    """Return a structlog logger, configuring defaults on first use."""
    if not _configured:
        configure_logging()
    return structlog.get_logger(name)


def tool_logger(tool: str):
    """Bind tool name and a fresh correlation id for one tool call (OBS-003)."""
    return get_logger().bind(tool=tool, correlation_id=uuid.uuid4().hex[:12])
