"""Request Validation Tests."""
import pytest
from ..core import SchemaValidator, FieldRule
from ..interfaces import ValidationResult


def test_required_field_missing():
    validator = SchemaValidator([FieldRule("email", required=True)])
    result = validator.validate({})
    assert result.valid is False
    assert any("required" in e for e in result.errors)


def test_type_validation():
    validator = SchemaValidator([FieldRule("age", field_type=int)])
    result = validator.validate({"age": "not_an_int"})
    assert result.valid is False


def test_min_length():
    validator = SchemaValidator([FieldRule("name", min_length=3)])
    result = validator.validate({"name": "ab"})
    assert result.valid is False


def test_pattern_validation():
    validator = SchemaValidator([FieldRule("email", pattern=r".+@.+\..+")])
    assert validator.validate({"email": "test@example.com"}).valid is True
    assert validator.validate({"email": "not-an-email"}).valid is False


def test_valid_data():
    validator = SchemaValidator([
        FieldRule("name", required=True, min_length=2),
        FieldRule("age", required=True, field_type=int),
    ])
    result = validator.validate({"name": "Alice", "age": 30})
    assert result.valid is True
