"""Error Handling Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type


class ErrorHandler(ABC):
    @abstractmethod
    def handle(self, error: Exception, context: Optional[Any] = None) -> None: ...


class ErrorClassifier(ABC):
    @abstractmethod
    def classify(self, error: Exception) -> str: ...
