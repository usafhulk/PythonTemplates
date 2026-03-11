"""Rate Limiter Configuration."""
from dataclasses import dataclass


@dataclass
class RateLimiterSettings:
    strategy: str = "token_bucket"
    rate: float = 100.0
    capacity: float = 200.0
    window_seconds: float = 60.0
    max_requests: int = 100
