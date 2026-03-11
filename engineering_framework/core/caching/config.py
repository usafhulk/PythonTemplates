"""Caching Configuration."""
from dataclasses import dataclass


@dataclass
class CacheSettings:
    backend: str = "inmemory"
    default_ttl: int = 300
    max_size: int = 1000
    redis_url: str = "redis://localhost:6379"
