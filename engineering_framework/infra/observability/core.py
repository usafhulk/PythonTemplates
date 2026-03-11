"""Observability Core."""
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from .interfaces import ObservabilityFacade, Span, Tracer

logger = logging.getLogger(__name__)


class InMemoryTracer(Tracer):
    def __init__(self) -> None:
        self._spans: List[Span] = []
        self._current_trace_id: Optional[str] = None

    def start_span(self, operation: str, tags: Optional[Dict[str, str]] = None) -> Span:
        trace_id = self._current_trace_id or str(uuid.uuid4())
        self._current_trace_id = trace_id
        return Span(trace_id=trace_id, span_id=str(uuid.uuid4()), operation=operation,
                    start_time=time.perf_counter(), tags=tags or {})

    def finish_span(self, span: Span, error: Optional[str] = None) -> None:
        span.end_time = time.perf_counter()
        span.error = error
        self._spans.append(span)

    @contextmanager
    def span(self, operation: str, **tags: str) -> Generator[Span, None, None]:
        s = self.start_span(operation, tags=tags)
        try:
            yield s
            self.finish_span(s)
        except Exception as e:
            self.finish_span(s, error=str(e))
            raise

    def get_spans(self) -> List[Span]:
        return list(self._spans)


class DefaultObservabilityFacade(ObservabilityFacade):
    def __init__(self, tracer: Optional[Tracer] = None) -> None:
        self._tracer = tracer or InMemoryTracer()
        self._metrics: Dict[str, float] = {}

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        self._metrics[name] = value

    def log(self, level: str, message: str, **context: Any) -> None:
        getattr(logger, level.lower(), logger.info)(message, extra={"context": context})

    def get_metrics(self) -> Dict[str, float]:
        return dict(self._metrics)
