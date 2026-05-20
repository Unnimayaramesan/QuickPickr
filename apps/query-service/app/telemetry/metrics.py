"""OpenTelemetry-compatible metric hooks + in-memory counters for local dev."""

from __future__ import annotations

from typing import Any

_metrics_available = False
try:
    from opentelemetry import metrics as otel_metrics  # type: ignore[import-untyped]

    _ = otel_metrics.get_meter_provider
    _metrics_available = True
except Exception:  # pragma: no cover
    otel_metrics = None  # type: ignore[misc]


_counters: dict[str, float] = {}


def _incr(name: str, value: float = 1.0) -> None:
    _counters[name] = _counters.get(name, 0.0) + value


def record_search_latency_ms(latency_ms: int) -> None:
    """search_latency_ms aggregate (histogram via OTLP in prod exporters)."""
    _incr("__search_latency_ms_sum", float(latency_ms))
    _incr("__search_latency_ms_count", 1.0)


def record_parse_failure(retailer: str) -> None:
    _incr(f"parse_failure_rate{{{retailer}}}", 1.0)


def record_zero_result_city(city_hint: str) -> None:
    _incr(f"zero_result_rate{{{city_hint}}}", 1.0)


def record_cache_hit(hit: bool) -> None:
    _incr("__cache_hit" if hit else "__cache_miss", 1.0)


def record_retailer_timeout(retailer: str) -> None:
    _incr(f"retailer_timeout_rate{{{retailer}}}", 1.0)


def record_freshness_age_minutes(minutes_age: float) -> None:
    _incr("__freshness_age_minutes_sum", minutes_age)
    _incr("__freshness_age_minutes_count", 1.0)


def debug_counters() -> dict[str, Any]:
    data = dict(_counters)
    data["otel_sdk_present"] = _metrics_available
    return data


__all__ = [
    "debug_counters",
    "record_cache_hit",
    "record_freshness_age_minutes",
    "record_parse_failure",
    "record_retailer_timeout",
    "record_search_latency_ms",
    "record_zero_result_city",
]
