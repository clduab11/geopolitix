"""Caching utilities for API responses."""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional

from cachetools import TTLCache

from config.settings import Settings

# Global cache instance
_cache = TTLCache(
    maxsize=Settings.CACHE_MAX_SIZE,
    ttl=Settings.CACHE_TTL_MINUTES * 60,
)


def _generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a unique cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(ttl_minutes: Optional[int] = None) -> Callable:
    """
    Decorator to cache function responses.

    Args:
        ttl_minutes: Custom TTL in minutes (uses default if None)

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{func.__name__}:{_generate_cache_key(*args, **kwargs)}"

            # Check cache
            if cache_key in _cache:
                return _cache[cache_key]

            # Call function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = result

            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Clear all cached responses."""
    _cache.clear()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "size": len(_cache),
        "maxsize": _cache.maxsize,
        "ttl": _cache.ttl,
    }


def remove_from_cache(key: str) -> bool:
    """
    Remove a specific key from cache.

    Args:
        key: Cache key to remove

    Returns:
        True if key was removed, False if not found
    """
    if key in _cache:
        del _cache[key]
        return True
    return False
