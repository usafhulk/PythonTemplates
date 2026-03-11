"""Caching Core."""
import logging
import threading
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from .interfaces import Cache

logger = logging.getLogger(__name__)


class InMemoryCache(Cache):
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store:
                return None
            value, expires_at = self._store[key]
            if expires_at is not None and time.time() > expires_at:
                del self._store[key]
                logger.debug("Cache miss (expired): %s", key)
                return None
            logger.debug("Cache hit: %s", key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = time.time() + ttl if ttl is not None else None
        with self._lock:
            self._store[key] = (value, expires_at)
        logger.debug("Cache set: %s (ttl=%s)", key, ttl)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


def cached(cache: Cache, key_fn: Optional[Callable[..., str]] = None, ttl: Optional[int] = None) -> Callable:
    """Decorator to cache function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = key_fn(*args, **kwargs) if key_fn else f"{func.__name__}:{args}:{kwargs}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
