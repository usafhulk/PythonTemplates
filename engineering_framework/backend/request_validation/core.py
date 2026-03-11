"""Request Validation Core."""
import logging
import re
from typing import Any, Callable, Dict, List, Optional

from .interfaces import ValidationResult, Validator

logger = logging.getLogger(__name__)


class FieldRule:
    def __init__(self, field_name: str, required: bool = False,
                 field_type: Optional[type] = None,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 pattern: Optional[str] = None,
                 custom: Optional[Callable[[Any], bool]] = None) -> None:
        self.field_name = field_name
        self.required = required
        self.field_type = field_type
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.custom = custom


class SchemaValidator(Validator):
    def __init__(self, rules: List[FieldRule]) -> None:
        self._rules = rules

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        for rule in self._rules:
            value = data.get(rule.field_name)
            if rule.required and value is None:
                errors.append(f"'{rule.field_name}' is required")
                continue
            if value is None:
                continue
            if rule.field_type and not isinstance(value, rule.field_type):
                errors.append(f"'{rule.field_name}' must be of type {rule.field_type.__name__}")
            if rule.min_length and isinstance(value, (str, list)) and len(value) < rule.min_length:
                errors.append(f"'{rule.field_name}' must have min length {rule.min_length}")
            if rule.max_length and isinstance(value, (str, list)) and len(value) > rule.max_length:
                errors.append(f"'{rule.field_name}' must have max length {rule.max_length}")
            if rule.pattern and isinstance(value, str) and not re.match(rule.pattern, value):
                errors.append(f"'{rule.field_name}' does not match pattern {rule.pattern}")
            if rule.custom and not rule.custom(value):
                errors.append(f"'{rule.field_name}' failed custom validation")
        valid = len(errors) == 0
        if not valid:
            logger.debug("Validation failed: %s", errors)
        return ValidationResult(valid=valid, errors=errors)
