"""Model Monitoring Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MonitoringAlert:
    alert_type: str
    model_name: str
    metric_name: str
    current_value: float
    threshold: float
    message: str


@dataclass
class ModelMonitoringReport:
    model_name: str
    total_predictions: int
    alerts: List[MonitoringAlert] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    healthy: bool = True


class ModelMonitor(ABC):
    @abstractmethod
    def record_prediction(self, model_name: str, prediction: Any, ground_truth: Optional[Any] = None) -> None: ...

    @abstractmethod
    def get_report(self, model_name: str) -> ModelMonitoringReport: ...
