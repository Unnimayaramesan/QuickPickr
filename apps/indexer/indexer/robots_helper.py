"""Respect crawl politeness hints (minimal robots.txt check)."""

from __future__ import annotations

import asyncio
import urllib.parse
import urllib.robotparser as robotparser


async def respectful_delay(origin_url: str, fallback_seconds: float) -> float:
    """Return seconds to sleep before hitting `origin_url` again."""

    def _read() -> float:
        try:
            parsed = urllib.parse.urlparse(origin_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urllib.parse.urljoin(base, "/robots.txt")
            rp = robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            delay = rp.crawl_delay("*")
            if delay and delay > 0:
                return float(delay)
        except Exception:
            pass
        return float(fallback_seconds)

    return await asyncio.to_thread(_read)
