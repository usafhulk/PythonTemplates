"""Plugin Architecture Configuration."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PluginSettings:
    plugin_dirs: List[str] = field(default_factory=list)
    auto_load: bool = True
    strict_validation: bool = False
