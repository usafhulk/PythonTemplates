"""Health Check Example."""
from engineering_framework.core.health_check.core import HealthCheckService, LivenessCheck

service = HealthCheckService()
service.register(LivenessCheck())
results = service.run_all()
for name, result in results.items():
    print(f"{name}: {result.status.value} - {result.message}")
print(f"Overall: {service.overall_status().value}")
