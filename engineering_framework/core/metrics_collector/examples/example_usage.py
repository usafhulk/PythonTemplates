"""Metrics Collector Example."""
from engineering_framework.core.metrics_collector.core import InMemoryMetricsCollector

metrics = InMemoryMetricsCollector()
metrics.counter("http_requests_total", labels={"method": "GET", "path": "/api/users"})
metrics.gauge("active_connections", 42.0)
with metrics.timer("db_query_duration"):
    pass  # simulate db call
print(metrics.get_metrics())
