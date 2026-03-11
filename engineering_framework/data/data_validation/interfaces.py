"""Data Validation Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DataValidationResult:
    passed: bool
    total_records: int
    failed_records: int
    errors: List[Dict[str, Any]] = field(default_factory=list)


class DataValidator(ABC):
    @abstractmethod
    def validate_record(self, record: Dict[str, Any]) -> List[str]: ...

    @abstractmethod
    def validate_dataset(self, records: List[Dict[str, Any]]) -> DataValidationResult: ...
