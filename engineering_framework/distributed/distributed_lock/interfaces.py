"""Distributed Lock Interfaces."""
from abc import ABC, abstractmethod


class DistributedLock(ABC):
    @abstractmethod
    def acquire(self, name: str, ttl_seconds: int = 30) -> bool: ...

    @abstractmethod
    def release(self, name: str) -> None: ...

    @abstractmethod
    def is_locked(self, name: str) -> bool: ...
