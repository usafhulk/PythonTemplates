"""Config Service Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class ConfigService(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def watch(self, key: str, callback: Callable[[str, Any], None]) -> None: ...

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]: ...
