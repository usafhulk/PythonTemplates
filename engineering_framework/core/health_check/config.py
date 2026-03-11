"""Health Check Configuration."""
from dataclasses import dataclass


@dataclass
class HealthCheckSettings:
    endpoint: str = "/health"
    interval_seconds: int = 30
    timeout_seconds: float = 5.0
