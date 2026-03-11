"""Config Manager Example."""
from engineering_framework.core.config_manager.core import DefaultConfigManager, EnvConfigSource

mgr = DefaultConfigManager()
mgr.add_source(EnvConfigSource(prefix="APP"))
mgr.set("debug", True)
print(mgr.get("debug"))
print(mgr.get("missing_key", "fallback"))
