"""Structured logging helpers; never emit full Indian pincodes (SAD §8.3)."""

from __future__ import annotations

import logging

_log = logging.getLogger("quickpickr.query")


def pincode_prefix(pincode: str) -> str:
    """First 3 digits only for logs (rest redacted)."""
    if not pincode or len(pincode) < 3:
        return "***"
    return f"{pincode[:3]}***"


def log_search_start(query: str, pincode_prefix_value: str) -> None:
    _log.info("search_started", extra={"query": query[:80], "pincode_prefix": pincode_prefix_value})


def log_search_done(
    query: str,
    pincode_prefix_value: str,
    latency_ms: int,
    cache_hit: bool,
    retailers_hit: int,
) -> None:
    _log.info(
        "search_completed",
        extra={
            "query": query[:80],
            "pincode_prefix": pincode_prefix_value,
            "latency_ms": latency_ms,
            "cache_hit": cache_hit,
            "retailers_hit": retailers_hit,
        },
    )
