"""Config Service Example."""
from engineering_framework.infra.config_service.core import InMemoryConfigService

svc = InMemoryConfigService({"log_level": "INFO"})
svc.watch("log_level", lambda k, v: print(f"Config changed: {k}={v}"))
svc.set("log_level", "DEBUG")
print(svc.snapshot())
