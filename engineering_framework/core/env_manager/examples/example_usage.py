"""Environment Manager Example."""
from engineering_framework.core.env_manager.core import DefaultEnvironmentManager
from engineering_framework.core.env_manager.interfaces import Environment

mgr = DefaultEnvironmentManager()
mgr.set(Environment.PRODUCTION)
print(f"Env: {mgr.current().value}")
print(f"Is prod: {mgr.is_production()}")
print(f"Is dev: {mgr.is_development()}")
