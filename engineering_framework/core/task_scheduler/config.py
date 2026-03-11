"""Task Scheduler Configuration."""
from dataclasses import dataclass


@dataclass
class SchedulerSettings:
    backend: str = "interval"
    timezone: str = "UTC"
    max_concurrent_jobs: int = 10
