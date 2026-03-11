"""Retry and Circuit Breaker Core."""
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

from .interfaces import CircuitBreaker, RetryPolicy

logger = logging.getLogger(__name__)


class ExponentialBackoffRetry(RetryPolicy):
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exc = e
                if attempt == self.max_attempts:
                    break
                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                logger.warning("Attempt %d failed: %s. Retrying in %.1fs", attempt, e, delay)
                time.sleep(delay)
        raise last_exc  # type: ignore[misc]


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class DefaultCircuitBreaker(CircuitBreaker):
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold
        self._failure_count = 0
        self._success_count = 0
        self._state = CircuitState.CLOSED
        self._opened_at: Optional[float] = None

    def state(self) -> str:
        return self._state.value

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self._state == CircuitState.OPEN:
            if time.time() - (self._opened_at or 0) > self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("Circuit breaker half-open")
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._success_threshold:
                self._state = CircuitState.CLOSED
                logger.info("Circuit breaker closed")

    def _on_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.time()
            logger.error("Circuit breaker opened after %d failures", self._failure_count)
