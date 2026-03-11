"""Metrics Collector Configuration."""
from dataclasses import dataclass


@dataclass
class MetricsSettings:
    backend: str = "inmemory"
    prometheus_port: int = 9090
    namespace: str = "app"
    enabled: bool = True
