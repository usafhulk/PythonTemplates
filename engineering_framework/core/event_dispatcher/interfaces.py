"""Event Dispatcher Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class Event:
    def __init__(self, name: str, data: Any = None) -> None:
        self.name = name
        self.data = data


class EventDispatcher(ABC):
    @abstractmethod
    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None: ...

    @abstractmethod
    def unsubscribe(self, event_name: str, handler: Callable[[Event], None]) -> None: ...

    @abstractmethod
    def dispatch(self, event: Event) -> None: ...
