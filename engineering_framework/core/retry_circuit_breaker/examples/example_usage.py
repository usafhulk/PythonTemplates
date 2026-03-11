"""Retry / Circuit Breaker Example."""
from engineering_framework.core.retry_circuit_breaker.core import (
    ExponentialBackoffRetry, DefaultCircuitBreaker
)

retry = ExponentialBackoffRetry(max_attempts=3, base_delay=0.1)
cb = DefaultCircuitBreaker(failure_threshold=3)

def unreliable_api_call():
    return {"data": "result"}

result = retry.execute(cb.call, unreliable_api_call)
print(result)
