"""Distributed Lock Configuration."""
from dataclasses import dataclass


@dataclass
class DistributedLockSettings:
    backend: str = "inmemory"
    redis_url: str = "redis://localhost:6379"
    default_ttl_seconds: int = 30
