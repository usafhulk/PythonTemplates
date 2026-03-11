"""Load Testing Configuration."""
from dataclasses import dataclass


@dataclass
class LoadTestSettings:
    concurrent_users: int = 10
    requests_per_user: int = 100
    ramp_up_seconds: float = 5.0
    think_time_ms: float = 0.0
    timeout_seconds: float = 30.0
