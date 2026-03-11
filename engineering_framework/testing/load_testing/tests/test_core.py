"""Load Testing Tests."""
import pytest
from ..core import FunctionScenario, LoadTestRunner
from ..interfaces import LoadTestConfig


def test_successful_load_test():
    config = LoadTestConfig(concurrent_users=3, requests_per_user=5)
    scenario = FunctionScenario(lambda: None)
    runner = LoadTestRunner(config)
    result = runner.run(scenario)
    assert result.total_requests == 15
    assert result.successful == 15
    assert result.failed == 0


def test_failing_scenario():
    config = LoadTestConfig(concurrent_users=2, requests_per_user=3)
    scenario = FunctionScenario(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
    runner = LoadTestRunner(config)
    result = runner.run(scenario)
    assert result.failed == 6
    assert result.successful == 0


def test_latency_stats():
    config = LoadTestConfig(concurrent_users=2, requests_per_user=5)
    scenario = FunctionScenario(lambda: None)
    runner = LoadTestRunner(config)
    result = runner.run(scenario)
    assert result.avg_latency_ms >= 0
    assert result.p95_latency_ms >= 0
    assert result.rps > 0
