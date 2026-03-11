"""Observability Configuration."""
from dataclasses import dataclass


@dataclass
class ObservabilitySettings:
    tracing_enabled: bool = True
    metrics_enabled: bool = True
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831
    otel_endpoint: str = "http://localhost:4317"
