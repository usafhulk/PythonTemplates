"""Structured Logging Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class StructuredLogger(ABC):
    """Abstract structured logger."""

    @abstractmethod
    def info(self, message: str, **context: Any) -> None: ...

    @abstractmethod
    def warning(self, message: str, **context: Any) -> None: ...

    @abstractmethod
    def error(self, message: str, **context: Any) -> None: ...

    @abstractmethod
    def debug(self, message: str, **context: Any) -> None: ...

    @abstractmethod
    def bind(self, **context: Any) -> "StructuredLogger": ...
