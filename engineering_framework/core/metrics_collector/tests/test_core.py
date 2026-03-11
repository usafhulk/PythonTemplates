"""Metrics Collector Tests."""
import time
import pytest
from ..core import InMemoryMetricsCollector


def test_counter():
    m = InMemoryMetricsCollector()
    m.counter("requests")
    m.counter("requests")
    metrics = m.get_metrics()
    assert metrics["counters"]["requests"] == 2.0


def test_gauge():
    m = InMemoryMetricsCollector()
    m.gauge("memory_mb", 512.0)
    metrics = m.get_metrics()
    assert metrics["gauges"]["memory_mb"] == 512.0


def test_histogram():
    m = InMemoryMetricsCollector()
    m.histogram("latency_s", 0.1)
    m.histogram("latency_s", 0.2)
    metrics = m.get_metrics()
    assert metrics["histograms"]["latency_s"]["count"] == 2


def test_timer():
    m = InMemoryMetricsCollector()
    with m.timer("operation_duration"):
        time.sleep(0.01)
    metrics = m.get_metrics()
    assert metrics["histograms"]["operation_duration"]["count"] == 1


def test_labels():
    m = InMemoryMetricsCollector()
    m.counter("requests", labels={"method": "GET", "status": "200"})
    metrics = m.get_metrics()
    assert any("method=GET" in k for k in metrics["counters"])
