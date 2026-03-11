"""Model Monitoring Configuration."""
from dataclasses import dataclass


@dataclass
class ModelMonitoringSettings:
    error_rate_threshold: float = 0.1
    drift_threshold: float = 0.3
    alert_channel: str = "log"
    monitoring_window: int = 1000
