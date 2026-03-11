"""Observability Tests."""
import pytest
from ..core import InMemoryTracer, DefaultObservabilityFacade


def test_span_tracking():
    tracer = InMemoryTracer()
    with tracer.span("db_query") as span:
        pass
    spans = tracer.get_spans()
    assert len(spans) == 1
    assert spans[0].operation == "db_query"
    assert spans[0].duration_ms >= 0


def test_span_error_recording():
    tracer = InMemoryTracer()
    try:
        with tracer.span("fail_op") as span:
            raise RuntimeError("db error")
    except RuntimeError:
        pass
    assert tracer.get_spans()[0].error == "db error"


def test_observability_facade():
    facade = DefaultObservabilityFacade()
    facade.record_metric("request_count", 42.0)
    assert facade.get_metrics()["request_count"] == 42.0
