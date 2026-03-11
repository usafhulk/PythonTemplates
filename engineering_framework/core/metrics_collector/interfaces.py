"""Metrics Collector Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MetricsCollector(ABC):
    @abstractmethod
    def counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None: ...

    @abstractmethod
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None: ...

    @abstractmethod
    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None: ...

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]: ...
