"""Feature Store Configuration."""
from dataclasses import dataclass


@dataclass
class FeatureStoreSettings:
    backend: str = "inmemory"
    redis_url: str = "redis://localhost:6379"
    ttl_seconds: int = 86400
    online_store: bool = True
    offline_store: bool = True
