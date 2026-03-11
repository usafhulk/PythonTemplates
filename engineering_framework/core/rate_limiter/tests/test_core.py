"""Rate Limiter Tests."""
import pytest
from ..core import TokenBucketRateLimiter, SlidingWindowRateLimiter


def test_token_bucket_allows_within_capacity():
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=10.0)
    assert limiter.acquire(5) is True
    assert limiter.acquire(5) is True


def test_token_bucket_denies_over_capacity():
    limiter = TokenBucketRateLimiter(rate=1.0, capacity=5.0)
    assert limiter.acquire(5) is True
    assert limiter.acquire(1) is False


def test_token_bucket_reset():
    limiter = TokenBucketRateLimiter(rate=1.0, capacity=5.0)
    limiter.acquire(5)
    limiter.reset()
    assert limiter.acquire(5) is True


def test_sliding_window_allows():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60.0)
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    assert limiter.acquire() is False


def test_sliding_window_reset():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60.0)
    limiter.acquire()
    limiter.reset()
    assert limiter.acquire() is True
