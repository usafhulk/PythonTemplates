"""Caching Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]: ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...
