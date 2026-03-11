"""Metrics Collector Core."""
import logging
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from .interfaces import MetricsCollector

logger = logging.getLogger(__name__)


class InMemoryMetricsCollector(MetricsCollector):
    """In-memory metrics collector (swap for Prometheus in production)."""

    def __init__(self) -> None:
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name

    def counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._make_key(name, labels)
        self._counters[key] += value
        logger.debug("counter %s += %s", key, value)

    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._make_key(name, labels)
        self._gauges[key] = value
        logger.debug("gauge %s = %s", key, value)

    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        logger.debug("histogram %s << %s", key, value)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: {"count": len(v), "sum": sum(v)} for k, v in self._histograms.items()},
        }

    @contextmanager
    def timer(self, name: str, labels: Optional[Dict[str, str]] = None) -> Generator[None, None, None]:
        """Context manager to time a block of code."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.histogram(name, elapsed, labels)
