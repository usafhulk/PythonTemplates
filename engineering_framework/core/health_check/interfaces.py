"""Health Check Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict = field(default_factory=dict)


class HealthCheck(ABC):
    @abstractmethod
    def check(self) -> HealthCheckResult: ...

    @property
    @abstractmethod
    def name(self) -> str: ...
