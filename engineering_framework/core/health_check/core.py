"""Health Check Core."""
import logging
import socket
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .interfaces import HealthCheck, HealthCheckResult, HealthStatus

logger = logging.getLogger(__name__)


class LivenessCheck(HealthCheck):
    """Basic liveness check - always returns healthy if process is running."""

    @property
    def name(self) -> str:
        return "liveness"

    def check(self) -> HealthCheckResult:
        return HealthCheckResult(name=self.name, status=HealthStatus.HEALTHY, message="Process is alive")


class DependencyHealthCheck(HealthCheck):
    """Check connectivity to a TCP dependency."""

    def __init__(self, check_name: str, host: str, port: int, timeout: float = 3.0) -> None:
        self._name = check_name
        self.host = host
        self.port = port
        self.timeout = timeout

    @property
    def name(self) -> str:
        return self._name

    def check(self) -> HealthCheckResult:
        try:
            sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            sock.close()
            return HealthCheckResult(name=self.name, status=HealthStatus.HEALTHY,
                                     message=f"{self.host}:{self.port} reachable")
        except OSError as e:
            return HealthCheckResult(name=self.name, status=HealthStatus.UNHEALTHY,
                                     message=str(e), details={"host": self.host, "port": self.port})


class HealthCheckService:
    """Aggregates multiple health checks."""

    def __init__(self) -> None:
        self._checks: List[HealthCheck] = []

    def register(self, check: HealthCheck) -> None:
        self._checks.append(check)
        logger.info("Registered health check: %s", check.name)

    def run_all(self) -> Dict[str, HealthCheckResult]:
        results = {}
        for check in self._checks:
            try:
                result = check.check()
            except Exception as e:
                result = HealthCheckResult(name=check.name, status=HealthStatus.UNHEALTHY, message=str(e))
            results[check.name] = result
            logger.debug("Health check %s: %s", check.name, result.status.value)
        return results

    def overall_status(self) -> HealthStatus:
        results = self.run_all()
        if all(r.status == HealthStatus.HEALTHY for r in results.values()):
            return HealthStatus.HEALTHY
        if any(r.status == HealthStatus.UNHEALTHY for r in results.values()):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED
