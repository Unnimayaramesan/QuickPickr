"""Per-session sliding-window rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, window_seconds: int) -> None:
        self.max_calls = max_calls
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, session_id: str) -> None:
        now = time.monotonic()
        bucket = self._hits[session_id]
        cutoff = now - float(self.window)
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)
        if len(bucket) >= self.max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded ({self.max_calls} requests per {self.window}s per session)",
            )
        bucket.append(now)

