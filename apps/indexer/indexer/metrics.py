"""Cheap in-process counters (Cloud Monitoring export via OTLP is future work)."""

from __future__ import annotations

from typing import Any

_counts: dict[str, float] = {}


def incr(name: str, value: float = 1.0) -> None:
    _counts[name] = _counts.get(name, 0.0) + float(value)


def snapshot() -> dict[str, Any]:
    return dict(_counts)
