"""Data Quality Configuration."""
from dataclasses import dataclass


@dataclass
class DataQualitySettings:
    alert_on_failure: bool = True
    max_null_rate: float = 0.05
    min_uniqueness: float = 0.9
    report_format: str = "json"
