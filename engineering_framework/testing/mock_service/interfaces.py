"""Mock Service Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class MockCall:
    method: str
    args: tuple
    kwargs: Dict[str, Any]
    return_value: Any


class MockService(ABC):
    @abstractmethod
    def setup_response(self, method: str, return_value: Any) -> None: ...

    @abstractmethod
    def call_count(self, method: str) -> int: ...

    @abstractmethod
    def was_called_with(self, method: str, *args: Any, **kwargs: Any) -> bool: ...
