"""Retry / Circuit Breaker Tests."""
import pytest
from unittest.mock import MagicMock
from ..core import ExponentialBackoffRetry, DefaultCircuitBreaker


def test_retry_succeeds_on_first_try():
    retry = ExponentialBackoffRetry(max_attempts=3, base_delay=0)
    mock = MagicMock(return_value="ok")
    result = retry.execute(mock)
    assert result == "ok"
    mock.assert_called_once()


def test_retry_retries_on_failure():
    retry = ExponentialBackoffRetry(max_attempts=3, base_delay=0)
    call_count = 0
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("fail")
        return "success"
    result = retry.execute(flaky)
    assert result == "success"
    assert call_count == 3


def test_retry_raises_after_max_attempts():
    retry = ExponentialBackoffRetry(max_attempts=2, base_delay=0)
    with pytest.raises(ValueError):
        retry.execute(lambda: (_ for _ in ()).throw(ValueError("always fails")))


def test_circuit_breaker_opens():
    cb = DefaultCircuitBreaker(failure_threshold=2, recovery_timeout=1000)
    def failing():
        raise RuntimeError("boom")
    for _ in range(2):
        try:
            cb.call(failing)
        except RuntimeError:
            pass
    assert cb.state() == "open"
    with pytest.raises(RuntimeError, match="OPEN"):
        cb.call(lambda: None)


def test_circuit_breaker_closed_on_success():
    cb = DefaultCircuitBreaker()
    cb.call(lambda: "ok")
    assert cb.state() == "closed"
