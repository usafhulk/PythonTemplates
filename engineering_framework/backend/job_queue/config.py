"""Job Queue Configuration."""
from dataclasses import dataclass


@dataclass
class JobQueueSettings:
    backend: str = "inmemory"
    worker_count: int = 2
    max_retries: int = 3
    visibility_timeout: int = 30
    redis_url: str = "redis://localhost:6379"
