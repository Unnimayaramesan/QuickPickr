"""In-module cache façade."""

from app.cache.redis_cache import get_or_compute

__all__ = ["get_or_compute"]
