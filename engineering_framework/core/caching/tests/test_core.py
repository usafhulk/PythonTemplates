"""Caching Tests."""
import time
import pytest
from ..core import InMemoryCache, cached


def test_cache_set_and_get():
    cache = InMemoryCache()
    cache.set("key", "value")
    assert cache.get("key") == "value"


def test_cache_miss():
    cache = InMemoryCache()
    assert cache.get("nonexistent") is None


def test_cache_ttl_expiry():
    cache = InMemoryCache()
    cache.set("key", "value", ttl=1)
    assert cache.get("key") == "value"
    time.sleep(1.1)
    assert cache.get("key") is None


def test_cache_delete():
    cache = InMemoryCache()
    cache.set("key", "value")
    cache.delete("key")
    assert cache.get("key") is None


def test_cached_decorator():
    cache = InMemoryCache()
    call_count = 0

    @cached(cache, ttl=60)
    def expensive_fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    assert expensive_fn(5) == 10
    assert expensive_fn(5) == 10
    assert call_count == 1
