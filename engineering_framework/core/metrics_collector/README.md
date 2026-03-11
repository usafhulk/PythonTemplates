# Metrics Collector

Collect application metrics: counters, gauges, histograms. Swap backend for Prometheus.

## Features
- Counter, gauge, histogram primitives
- Label support
- Timer context manager
- Pluggable backend

## Usage
```python
from engineering_framework.core.metrics_collector.core import InMemoryMetricsCollector
m = InMemoryMetricsCollector()
m.counter("requests", labels={"method": "GET"})
```
