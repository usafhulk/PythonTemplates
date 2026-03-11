"""Retry / Circuit Breaker Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryPolicy(ABC):
    @abstractmethod
    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any: ...


class CircuitBreaker(ABC):
    @abstractmethod
    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def state(self) -> str: ...
