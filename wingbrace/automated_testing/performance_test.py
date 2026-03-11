"""
performance_test.py
===================
Template for basic performance and load testing.

Measures response times, throughput, error rates, and percentile
latencies for any callable (functions, API calls, database queries, etc.)
without external dependencies.

Usage::

    from wingbrace.automated_testing import PerformanceTest

    perf = PerformanceTest(name="Login API")

    def call_login():
        # call your function / API here
        ...

    results = perf.run(call_login, iterations=200, concurrency=10)
    print(results.summary())

    # Assert that p95 latency is under 500 ms
    results.assert_p95_under(0.5)
"""

import concurrent.futures
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from wingbrace.utilities.logger import get_logger


@dataclass
class PerformanceResult:
    """
    Container for performance test results.

    Attributes
    ----------
    name:
        Descriptive name of the test.
    total_iterations:
        Number of iterations attempted.
    successes:
        Iterations that completed without raising an exception.
    failures:
        Iterations that raised an exception.
    durations:
        Elapsed time in seconds for each *successful* iteration.
    errors:
        Exception messages from failed iterations.
    """

    name: str
    total_iterations: int
    successes: int
    failures: int
    durations: list[float] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Computed statistics
    # ------------------------------------------------------------------

    @property
    def error_rate(self) -> float:
        """Fraction of iterations that failed (0.0–1.0)."""
        if self.total_iterations == 0:
            return 0.0
        return self.failures / self.total_iterations

    @property
    def min_latency(self) -> float:
        return min(self.durations) if self.durations else 0.0

    @property
    def max_latency(self) -> float:
        return max(self.durations) if self.durations else 0.0

    @property
    def mean_latency(self) -> float:
        return statistics.mean(self.durations) if self.durations else 0.0

    @property
    def median_latency(self) -> float:
        return statistics.median(self.durations) if self.durations else 0.0

    @property
    def stdev_latency(self) -> float:
        return statistics.stdev(self.durations) if len(self.durations) > 1 else 0.0

    def percentile(self, pct: float) -> float:
        """
        Return the *pct*-th percentile of latencies (0–100).

        Parameters
        ----------
        pct:
            Percentile to compute, e.g. ``95`` for the 95th percentile.
        """
        if not self.durations:
            return 0.0
        sorted_d = sorted(self.durations)
        index = int(len(sorted_d) * pct / 100)
        index = min(index, len(sorted_d) - 1)
        return sorted_d[index]

    @property
    def throughput(self) -> float:
        """Successful iterations per second."""
        total_time = sum(self.durations)
        if total_time == 0:
            return 0.0
        return self.successes / total_time

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def assert_error_rate_below(self, threshold: float) -> None:
        """Raise ``AssertionError`` if the error rate exceeds *threshold*."""
        if self.error_rate > threshold:
            raise AssertionError(
                f"[{self.name}] Error rate {self.error_rate:.2%} exceeds "
                f"threshold {threshold:.2%}"
            )

    def assert_mean_under(self, seconds: float) -> None:
        """Raise ``AssertionError`` if mean latency exceeds *seconds*."""
        if self.mean_latency > seconds:
            raise AssertionError(
                f"[{self.name}] Mean latency {self.mean_latency:.3f}s exceeds "
                f"limit {seconds}s"
            )

    def assert_p95_under(self, seconds: float) -> None:
        """Raise ``AssertionError`` if the 95th-percentile latency exceeds *seconds*."""
        p95 = self.percentile(95)
        if p95 > seconds:
            raise AssertionError(
                f"[{self.name}] P95 latency {p95:.3f}s exceeds limit {seconds}s"
            )

    def assert_p99_under(self, seconds: float) -> None:
        """Raise ``AssertionError`` if the 99th-percentile latency exceeds *seconds*."""
        p99 = self.percentile(99)
        if p99 > seconds:
            raise AssertionError(
                f"[{self.name}] P99 latency {p99:.3f}s exceeds limit {seconds}s"
            )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Return a human-readable summary string."""
        return (
            f"Performance Test: {self.name}\n"
            f"  Iterations : {self.total_iterations} "
            f"({self.successes} OK / {self.failures} ERR)\n"
            f"  Error Rate : {self.error_rate:.2%}\n"
            f"  Latency (s): min={self.min_latency:.3f}  mean={self.mean_latency:.3f}  "
            f"median={self.median_latency:.3f}  max={self.max_latency:.3f}  "
            f"p95={self.percentile(95):.3f}  p99={self.percentile(99):.3f}\n"
            f"  Throughput : {self.throughput:.1f} req/s\n"
            f"  Std Dev    : {self.stdev_latency:.4f}s"
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the results as a plain dictionary."""
        return {
            "name": self.name,
            "total_iterations": self.total_iterations,
            "successes": self.successes,
            "failures": self.failures,
            "error_rate": round(self.error_rate, 4),
            "latency": {
                "min": round(self.min_latency, 4),
                "mean": round(self.mean_latency, 4),
                "median": round(self.median_latency, 4),
                "max": round(self.max_latency, 4),
                "p95": round(self.percentile(95), 4),
                "p99": round(self.percentile(99), 4),
                "stdev": round(self.stdev_latency, 4),
            },
            "throughput_per_sec": round(self.throughput, 2),
            "errors": self.errors[:10],  # cap to first 10
        }


class PerformanceTest:
    """
    Run a callable under load and collect latency/error statistics.

    Parameters
    ----------
    name:
        Descriptive name used in result summaries.
    """

    def __init__(self, name: str = "Performance Test") -> None:
        self.name = name
        self.log = get_logger(self.__class__.__name__)

    def run(
        self,
        func: Callable[[], Any],
        iterations: int = 100,
        concurrency: int = 1,
        warmup: int = 0,
    ) -> PerformanceResult:
        """
        Execute *func* for *iterations* calls with *concurrency* workers.

        Parameters
        ----------
        func:
            Zero-argument callable to benchmark.
        iterations:
            Total number of calls to make.
        concurrency:
            Number of concurrent threads (workers).
        warmup:
            Number of warm-up calls to make *before* measuring.  Warm-up
            results are discarded.

        Returns
        -------
        PerformanceResult
            Aggregated result containing all timing and error information.
        """
        # Warm-up phase (results discarded)
        if warmup > 0:
            self.log.info("Running %d warm-up iteration(s)…", warmup)
            self._execute(func, warmup, concurrency)

        self.log.info(
            "Starting performance test '%s': %d iterations, concurrency=%d",
            self.name,
            iterations,
            concurrency,
        )

        raw_results = self._execute(func, iterations, concurrency)

        successes = 0
        failures = 0
        durations: list[float] = []
        errors: list[str] = []

        for ok, duration_or_err in raw_results:
            if ok:
                successes += 1
                durations.append(duration_or_err)  # type: ignore[arg-type]
            else:
                failures += 1
                errors.append(str(duration_or_err))

        result = PerformanceResult(
            name=self.name,
            total_iterations=iterations,
            successes=successes,
            failures=failures,
            durations=durations,
            errors=errors,
        )
        self.log.info(result.summary())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _execute(
        self,
        func: Callable[[], Any],
        iterations: int,
        concurrency: int,
    ) -> list[tuple[bool, Any]]:
        """Execute *func* *iterations* times using *concurrency* threads."""
        results: list[tuple[bool, Any]] = []

        def _timed_call() -> tuple[bool, Any]:
            start = time.monotonic()
            try:
                func()
                return True, time.monotonic() - start
            except Exception as exc:
                return False, str(exc)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency
        ) as executor:
            futures = [executor.submit(_timed_call) for _ in range(iterations)]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        return results
