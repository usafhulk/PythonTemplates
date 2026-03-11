"""Load Testing Example."""
from engineering_framework.testing.load_testing.core import FunctionScenario, LoadTestRunner
from engineering_framework.testing.load_testing.interfaces import LoadTestConfig

config = LoadTestConfig(concurrent_users=5, requests_per_user=20)
counter = [0]

def simulated_api_call():
    counter[0] += 1

scenario = FunctionScenario(simulated_api_call)
runner = LoadTestRunner(config)
result = runner.run(scenario)

print(f"Total requests: {result.total_requests}")
print(f"Successful: {result.successful}")
print(f"Avg latency: {result.avg_latency_ms:.2f}ms")
print(f"P95 latency: {result.p95_latency_ms:.2f}ms")
print(f"RPS: {result.rps:.1f}")
