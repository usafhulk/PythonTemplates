"""Rate Limiter Core."""
import logging
import threading
import time
from typing import Optional

from .interfaces import RateLimiter

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            logger.warning("Rate limit exceeded: requested %d tokens, available %.2f", tokens, self._tokens)
            return False

    def reset(self) -> None:
        with self._lock:
            self._tokens = self.capacity
            self._last_refill = time.monotonic()


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window counter rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: list = []
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.monotonic()
            self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
            if len(self._timestamps) + tokens <= self.max_requests:
                self._timestamps.extend([now] * tokens)
                return True
            return False

    def reset(self) -> None:
        with self._lock:
            self._timestamps.clear()
