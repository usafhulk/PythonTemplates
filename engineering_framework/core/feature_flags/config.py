"""Feature Flags Configuration."""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class FeatureFlagSettings:
    provider: str = "inmemory"
    flags: Dict[str, bool] = field(default_factory=dict)
    remote_url: str = ""
