"""Observability Example."""
from engineering_framework.infra.observability.core import InMemoryTracer, DefaultObservabilityFacade

tracer = InMemoryTracer()
obs = DefaultObservabilityFacade(tracer)
with tracer.span("process_request", service="api") as span:
    obs.record_metric("latency_ms", 45.2)
spans = tracer.get_spans()
print(f"Duration: {spans[0].duration_ms:.2f}ms")
