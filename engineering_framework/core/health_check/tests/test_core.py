"""Health Check Tests."""
import pytest
from ..core import LivenessCheck, HealthCheckService, DependencyHealthCheck
from ..interfaces import HealthStatus


def test_liveness_check():
    check = LivenessCheck()
    result = check.check()
    assert result.status == HealthStatus.HEALTHY


def test_health_check_service_all_healthy():
    service = HealthCheckService()
    service.register(LivenessCheck())
    assert service.overall_status() == HealthStatus.HEALTHY


def test_dependency_check_unreachable():
    check = DependencyHealthCheck("redis", "localhost", 19999, timeout=0.5)
    result = check.check()
    assert result.status == HealthStatus.UNHEALTHY


def test_service_with_failing_check():
    service = HealthCheckService()
    service.register(LivenessCheck())
    service.register(DependencyHealthCheck("db", "localhost", 19998, timeout=0.5))
    assert service.overall_status() == HealthStatus.UNHEALTHY
