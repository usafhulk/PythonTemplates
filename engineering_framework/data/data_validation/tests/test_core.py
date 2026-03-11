"""Data Validation Tests."""
from typing import Optional
import pytest
from ..core import RuleBasedDataValidator, ColumnRule


def test_not_null_validation():
    validator = RuleBasedDataValidator([ColumnRule("id", not_null=True)])
    errors = validator.validate_record({"id": None})
    assert len(errors) > 0


def test_dtype_validation():
    validator = RuleBasedDataValidator([ColumnRule("age", dtype=int)])
    errors = validator.validate_record({"age": "thirty"})
    assert len(errors) > 0


def test_range_validation():
    validator = RuleBasedDataValidator([ColumnRule("score", min_value=0, max_value=100)])
    assert validator.validate_record({"score": 50}) == []
    assert len(validator.validate_record({"score": 150})) > 0


def test_dataset_validation():
    validator = RuleBasedDataValidator([ColumnRule("name", not_null=True)])
    records = [{"name": "Alice"}, {"name": None}, {"name": "Bob"}]
    result = validator.validate_dataset(records)
    assert result.total_records == 3
    assert result.failed_records == 1
    assert result.passed is False
