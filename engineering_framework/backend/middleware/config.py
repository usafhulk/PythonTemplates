"""Middleware Configuration."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class MiddlewareSettings:
    enabled: List[str] = field(default_factory=lambda: ["logging", "request_id", "cors"])
    cors_origins: str = "*"
