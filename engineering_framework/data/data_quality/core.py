"""Data Quality Core."""
import logging
from typing import Any, Dict, List, Optional

from .interfaces import QualityCheck, QualityMetric, QualityReport

logger = logging.getLogger(__name__)


class NullRateCheck(QualityCheck):
    def __init__(self, column: str, max_null_rate: float = 0.05) -> None:
        self._column = column
        self._threshold = max_null_rate

    @property
    def name(self) -> str:
        return f"null_rate_{self._column}"

    def compute(self, records: List[Dict[str, Any]]) -> QualityMetric:
        if not records:
            return QualityMetric(name=self.name, value=0.0, threshold=self._threshold, passed=True)
        null_count = sum(1 for r in records if r.get(self._column) is None)
        rate = null_count / len(records)
        return QualityMetric(
            name=self.name, value=rate, threshold=self._threshold,
            passed=rate <= self._threshold,
            details={"null_count": null_count, "total": len(records)}
        )


class UniquenessCheck(QualityCheck):
    def __init__(self, column: str, min_uniqueness: float = 0.9) -> None:
        self._column = column
        self._threshold = min_uniqueness

    @property
    def name(self) -> str:
        return f"uniqueness_{self._column}"

    def compute(self, records: List[Dict[str, Any]]) -> QualityMetric:
        if not records:
            return QualityMetric(name=self.name, value=1.0, threshold=self._threshold, passed=True)
        values = [r.get(self._column) for r in records if r.get(self._column) is not None]
        unique_ratio = len(set(values)) / len(values) if values else 1.0
        return QualityMetric(
            name=self.name, value=unique_ratio, threshold=self._threshold,
            passed=unique_ratio >= self._threshold,
            details={"unique_values": len(set(values)), "total_values": len(values)}
        )


class DataQualityMonitor:
    def __init__(self, checks: Optional[List[QualityCheck]] = None) -> None:
        self._checks: List[QualityCheck] = checks or []

    def add_check(self, check: QualityCheck) -> "DataQualityMonitor":
        self._checks.append(check)
        return self

    def run(self, dataset_name: str, records: List[Dict[str, Any]]) -> QualityReport:
        metrics = []
        for check in self._checks:
            try:
                metric = check.compute(records)
                metrics.append(metric)
                status = "PASS" if metric.passed else "FAIL"
                logger.info("Quality check %s: %s (value=%.3f, threshold=%.3f)",
                           check.name, status, metric.value, metric.threshold)
            except Exception as e:
                logger.error("Quality check %s failed: %s", check.name, e)
        overall = all(m.passed for m in metrics)
        return QualityReport(
            dataset_name=dataset_name,
            total_records=len(records),
            metrics=metrics,
            overall_passed=overall,
        )
