"""Data Quality Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QualityMetric:
    name: str
    value: float
    threshold: float
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    dataset_name: str
    total_records: int
    metrics: List[QualityMetric] = field(default_factory=list)
    overall_passed: bool = True


class QualityCheck(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, records: List[Dict[str, Any]]) -> QualityMetric: ...
