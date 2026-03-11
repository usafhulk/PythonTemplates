"""Load Testing Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class LoadTestConfig:
    concurrent_users: int = 10
    requests_per_user: int = 10
    ramp_up_seconds: float = 0.0
    target_rps: Optional[float] = None


@dataclass
class LoadTestResult:
    total_requests: int
    successful: int
    failed: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    rps: float
    errors: List[str] = field(default_factory=list)


class LoadTestScenario(ABC):
    @abstractmethod
    def execute(self) -> bool: ...
