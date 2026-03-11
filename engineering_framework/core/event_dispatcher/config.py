"""Event Dispatcher Configuration."""
from dataclasses import dataclass


@dataclass
class EventDispatcherSettings:
    mode: str = "sync"
    max_handlers_per_event: int = 100
    error_strategy: str = "log"
