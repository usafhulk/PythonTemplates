"""Load Testing Core."""
import logging
import statistics
import threading
import time
from typing import Callable, List

from .interfaces import LoadTestConfig, LoadTestResult, LoadTestScenario

logger = logging.getLogger(__name__)


class FunctionScenario(LoadTestScenario):
    def __init__(self, func: Callable[[], None]) -> None:
        self._func = func

    def execute(self) -> bool:
        try:
            self._func()
            return True
        except Exception:
            return False


class LoadTestRunner:
    def __init__(self, config: LoadTestConfig) -> None:
        self._config = config

    def run(self, scenario: LoadTestScenario) -> LoadTestResult:
        latencies: List[float] = []
        errors: List[str] = []
        lock = threading.Lock()

        def worker() -> None:
            for _ in range(self._config.requests_per_user):
                start = time.perf_counter()
                success = scenario.execute()
                elapsed_ms = (time.perf_counter() - start) * 1000
                with lock:
                    latencies.append(elapsed_ms)
                    if not success:
                        errors.append("scenario_failed")

        threads = [threading.Thread(target=worker) for _ in range(self._config.concurrent_users)]
        start_time = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start_time

        total = len(latencies)
        sorted_latencies = sorted(latencies)

        def percentile(data: List[float], pct: float) -> float:
            if not data:
                return 0.0
            idx = int(len(data) * pct / 100)
            return data[min(idx, len(data) - 1)]

        return LoadTestResult(
            total_requests=total,
            successful=total - len(errors),
            failed=len(errors),
            avg_latency_ms=statistics.mean(latencies) if latencies else 0.0,
            p95_latency_ms=percentile(sorted_latencies, 95),
            p99_latency_ms=percentile(sorted_latencies, 99),
            rps=total / elapsed if elapsed > 0 else 0.0,
            errors=errors[:10],
        )
