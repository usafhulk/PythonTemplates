"""Dependency Injection Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

T = TypeVar("T")


class Container(ABC):
    @abstractmethod
    def register(self, interface: Type[T], implementation: Any, singleton: bool = True) -> None: ...

    @abstractmethod
    def resolve(self, interface: Type[T]) -> T: ...
