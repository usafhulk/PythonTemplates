"""
data_validator.py
=================
Schema and constraint validation for datasets (lists of dicts).

Supports:
    - Required field checks
    - Type validation
    - Regex pattern matching
    - Min/max length for strings
    - Numeric range checks
    - Allowed-values (enum) constraints
    - Custom callable validators
    - Aggregated validation reports

Usage::

    from wingbrace.data_cleanup import DataValidator

    schema = {
        "name":  {"type": str, "required": True, "min_length": 1, "max_length": 100},
        "age":   {"type": int, "required": True, "min_value": 0,  "max_value": 150},
        "email": {"type": str, "required": True, "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
        "role":  {"type": str, "allowed_values": ["admin", "user", "guest"]},
    }

    validator = DataValidator(schema)
    results = validator.validate(records)

    if results.is_valid:
        print("All records passed validation.")
    else:
        for error in results.errors:
            print(error)
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ValidationError:
    """Describes a single validation failure."""

    row_index: int
    field: str
    value: Any
    rule: str
    message: str

    def __str__(self) -> str:
        return (
            f"Row {self.row_index} | field={self.field!r} | "
            f"rule={self.rule} | value={self.value!r} | {self.message}"
        )


@dataclass
class ValidationResult:
    """Aggregated result of validating a dataset."""

    errors: list[ValidationError] = field(default_factory=list)
    total_rows: int = 0

    @property
    def is_valid(self) -> bool:
        """``True`` when there are no validation errors."""
        return len(self.errors) == 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def invalid_rows(self) -> set[int]:
        return {e.row_index for e in self.errors}

    def summary(self) -> str:
        lines = [
            f"Validation Result: {self.total_rows} rows checked, "
            f"{len(self.invalid_rows)} invalid, {self.error_count} error(s)."
        ]
        for err in self.errors[:50]:  # cap display to 50
            lines.append(f"  {err}")
        if self.error_count > 50:
            lines.append(f"  … and {self.error_count - 50} more error(s).")
        return "\n".join(lines)

    def errors_for_row(self, index: int) -> list[ValidationError]:
        return [e for e in self.errors if e.row_index == index]

    def errors_for_field(self, field_name: str) -> list[ValidationError]:
        return [e for e in self.errors if e.field == field_name]


class DataValidator:
    """
    Validate a list-of-dict dataset against a schema.

    Parameters
    ----------
    schema:
        A ``dict`` mapping field names to rule dicts.  Supported rule keys:

        ``required`` (bool)
            Field must be present and non-null.
        ``type`` (type)
            Value must be an instance of this type (after coercion attempt).
        ``min_value`` / ``max_value`` (int | float)
            Numeric range constraint.
        ``min_length`` / ``max_length`` (int)
            String length constraint.
        ``pattern`` (str)
            Regex the string value must fully match (``re.fullmatch``).
        ``allowed_values`` (list)
            Value must be in this list.
        ``custom`` (callable)
            A callable ``f(value) -> bool``.  Returns ``True`` if valid.
        ``custom_message`` (str)
            Error message used when the ``custom`` rule fails.

    allow_extra_fields:
        When ``False`` (default), extra fields not present in the schema
        are silently allowed.  Set to ``True`` to record errors for them.
    """

    def __init__(
        self,
        schema: dict[str, dict[str, Any]],
        allow_extra_fields: bool = True,
    ) -> None:
        self.schema = schema
        self.allow_extra_fields = allow_extra_fields

    def validate(self, data: list[dict[str, Any]]) -> ValidationResult:
        """
        Validate all rows in *data* against the schema.

        Returns
        -------
        ValidationResult
            Contains all errors found (empty if data is valid).
        """
        result = ValidationResult(total_rows=len(data))
        for idx, row in enumerate(data):
            self._validate_row(idx, row, result)
        return result

    def validate_one(
        self, row: dict[str, Any], row_index: int = 0
    ) -> ValidationResult:
        """Validate a single *row*."""
        result = ValidationResult(total_rows=1)
        self._validate_row(row_index, row, result)
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_row(
        self,
        idx: int,
        row: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        for fname, rules in self.schema.items():
            value = row.get(fname)
            present = fname in row and value is not None

            # --- required ---
            if rules.get("required") and not present:
                result.errors.append(
                    ValidationError(idx, fname, value, "required",
                                    f"Field '{fname}' is required but missing or null.")
                )
                continue  # further checks are meaningless without a value

            if not present:
                continue

            # --- type ---
            expected_type = rules.get("type")
            if expected_type is not None and not isinstance(value, expected_type):
                result.errors.append(
                    ValidationError(
                        idx, fname, value, "type",
                        f"Expected {expected_type.__name__}, got {type(value).__name__}."
                    )
                )

            # --- min_value / max_value ---
            if "min_value" in rules:
                try:
                    if float(value) < float(rules["min_value"]):
                        result.errors.append(
                            ValidationError(
                                idx, fname, value, "min_value",
                                f"Value {value} is below minimum {rules['min_value']}."
                            )
                        )
                except (TypeError, ValueError):
                    pass

            if "max_value" in rules:
                try:
                    if float(value) > float(rules["max_value"]):
                        result.errors.append(
                            ValidationError(
                                idx, fname, value, "max_value",
                                f"Value {value} exceeds maximum {rules['max_value']}."
                            )
                        )
                except (TypeError, ValueError):
                    pass

            # --- min_length / max_length ---
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    result.errors.append(
                        ValidationError(
                            idx, fname, value, "min_length",
                            f"String length {len(value)} is below minimum {rules['min_length']}."
                        )
                    )
                if "max_length" in rules and len(value) > rules["max_length"]:
                    result.errors.append(
                        ValidationError(
                            idx, fname, value, "max_length",
                            f"String length {len(value)} exceeds maximum {rules['max_length']}."
                        )
                    )

            # --- pattern ---
            if "pattern" in rules and isinstance(value, str):
                if not re.fullmatch(rules["pattern"], value):
                    result.errors.append(
                        ValidationError(
                            idx, fname, value, "pattern",
                            f"Value does not match pattern {rules['pattern']!r}."
                        )
                    )

            # --- allowed_values ---
            if "allowed_values" in rules and value not in rules["allowed_values"]:
                result.errors.append(
                    ValidationError(
                        idx, fname, value, "allowed_values",
                        f"Value {value!r} not in allowed set {rules['allowed_values']}."
                    )
                )

            # --- custom callable ---
            custom_fn: Callable[[Any], bool] | None = rules.get("custom")
            if custom_fn is not None:
                try:
                    passed = custom_fn(value)
                except Exception as exc:
                    passed = False
                    custom_msg = f"Custom validator raised {exc}"
                else:
                    custom_msg = rules.get("custom_message", "Custom validation failed.")
                if not passed:
                    result.errors.append(
                        ValidationError(idx, fname, value, "custom", custom_msg)
                    )

        # --- extra fields check ---
        if not self.allow_extra_fields:
            for fname in row:
                if fname not in self.schema:
                    result.errors.append(
                        ValidationError(
                            idx, fname, row[fname], "extra_field",
                            f"Field '{fname}' is not defined in the schema."
                        )
                    )
