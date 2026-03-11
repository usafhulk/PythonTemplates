"""Config Manager Configuration."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ConfigManagerSettings:
    config_file: str = "config.json"
    env_prefix: str = "APP"
    sources: List[str] = field(default_factory=lambda: ["env", "file"])
    cache_enabled: bool = True
