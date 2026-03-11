"""Data Validation Core."""
import logging
from typing import Any, Callable, Dict, List, Optional

from .interfaces import DataValidationResult, DataValidator

logger = logging.getLogger(__name__)


class ColumnRule:
    def __init__(self, column: str, not_null: bool = False,
                 dtype: Optional[type] = None,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 allowed_values: Optional[List[Any]] = None,
                 custom: Optional[Callable[[Any], bool]] = None) -> None:
        self.column = column
        self.not_null = not_null
        self.dtype = dtype
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
        self.custom = custom


class RuleBasedDataValidator(DataValidator):
    def __init__(self, rules: List[ColumnRule]) -> None:
        self._rules = rules

    def validate_record(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        for rule in self._rules:
            value = record.get(rule.column)
            if rule.not_null and value is None:
                errors.append(f"Column '{rule.column}' is null")
                continue
            if value is None:
                continue
            if rule.dtype and not isinstance(value, rule.dtype):
                errors.append(f"Column '{rule.column}' expected {rule.dtype.__name__}, got {type(value).__name__}")
            if rule.min_value is not None and isinstance(value, (int, float)) and value < rule.min_value:
                errors.append(f"Column '{rule.column}' below min {rule.min_value}")
            if rule.max_value is not None and isinstance(value, (int, float)) and value > rule.max_value:
                errors.append(f"Column '{rule.column}' above max {rule.max_value}")
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(f"Column '{rule.column}' value '{value}' not in allowed values")
            if rule.custom and not rule.custom(value):
                errors.append(f"Column '{rule.column}' failed custom validation")
        return errors

    def validate_dataset(self, records: List[Dict[str, Any]]) -> DataValidationResult:
        all_errors = []
        failed = 0
        for i, record in enumerate(records):
            errs = self.validate_record(record)
            if errs:
                failed += 1
                all_errors.append({"record_index": i, "errors": errs})
        return DataValidationResult(
            passed=failed == 0,
            total_records=len(records),
            failed_records=failed,
            errors=all_errors,
        )
