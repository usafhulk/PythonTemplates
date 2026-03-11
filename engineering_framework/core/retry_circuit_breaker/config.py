"""Retry/Circuit Breaker Configuration."""
from dataclasses import dataclass


@dataclass
class RetrySettings:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0


@dataclass
class CircuitBreakerSettings:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    success_threshold: int = 2
