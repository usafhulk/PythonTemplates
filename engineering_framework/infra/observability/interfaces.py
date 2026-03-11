"""Observability Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Span:
    trace_id: str
    span_id: str
    operation: str
    start_time: float
    end_time: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


class Tracer(ABC):
    @abstractmethod
    def start_span(self, operation: str, tags: Optional[Dict[str, str]] = None) -> Span: ...

    @abstractmethod
    def finish_span(self, span: Span, error: Optional[str] = None) -> None: ...


class ObservabilityFacade(ABC):
    @abstractmethod
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None: ...

    @abstractmethod
    def log(self, level: str, message: str, **context: Any) -> None: ...
