# Config Manager

Centralized configuration management supporting environment variables, files, and runtime overrides.

## Features
- Layered config sources (env, file, remote)
- Runtime overrides
- Caching for performance
- Extensible via ConfigSource interface

## Usage
```python
from engineering_framework.core.config_manager.core import DefaultConfigManager, EnvConfigSource
mgr = DefaultConfigManager()
mgr.add_source(EnvConfigSource(prefix="APP"))
value = mgr.get("database_url", "sqlite:///default.db")
```

## Extension
Implement `ConfigSource` to add remote config (Consul, AWS SSM, etc.).
