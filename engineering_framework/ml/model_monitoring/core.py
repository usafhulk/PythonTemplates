"""Model Monitoring Core."""
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .interfaces import ModelMonitor, ModelMonitoringReport, MonitoringAlert

logger = logging.getLogger(__name__)


class InMemoryModelMonitor(ModelMonitor):
    """In-memory model performance monitor."""

    def __init__(self, error_rate_threshold: float = 0.1,
                 drift_threshold: float = 0.3) -> None:
        self._error_rate_threshold = error_rate_threshold
        self._drift_threshold = drift_threshold
        self._predictions: Dict[str, List[Any]] = defaultdict(list)
        self._ground_truths: Dict[str, List[Any]] = defaultdict(list)
        self._errors: Dict[str, int] = defaultdict(int)

    def record_prediction(self, model_name: str, prediction: Any, ground_truth: Optional[Any] = None) -> None:
        self._predictions[model_name].append(prediction)
        if ground_truth is not None:
            self._ground_truths[model_name].append(ground_truth)
            if prediction != ground_truth:
                self._errors[model_name] += 1
        logger.debug("Prediction recorded for model: %s", model_name)

    def get_report(self, model_name: str) -> ModelMonitoringReport:
        preds = self._predictions[model_name]
        total = len(preds)
        alerts: List[MonitoringAlert] = []
        metrics: Dict[str, float] = {}

        if total > 0:
            error_rate = self._errors[model_name] / total
            metrics["error_rate"] = error_rate
            if error_rate > self._error_rate_threshold:
                alerts.append(MonitoringAlert(
                    alert_type="high_error_rate",
                    model_name=model_name,
                    metric_name="error_rate",
                    current_value=error_rate,
                    threshold=self._error_rate_threshold,
                    message=f"Error rate {error_rate:.2%} exceeds threshold {self._error_rate_threshold:.2%}",
                ))

        return ModelMonitoringReport(
            model_name=model_name,
            total_predictions=total,
            alerts=alerts,
            metrics=metrics,
            healthy=len(alerts) == 0,
        )
