"""
data_cleaner.py
===============
Template for cleaning raw datasets represented as lists of dictionaries
(rows) or plain Python lists/values.

Handles:
    - Missing / null values (fill, drop, or flag)
    - Duplicate rows
    - Whitespace stripping and case normalisation for string fields
    - Type coercion (int, float, bool, datetime)
    - Value range clamping
    - Configurable field-level rules via ``CleaningConfig``

Usage::

    from wingbrace.data_cleanup import DataCleaner

    raw = [
        {"name": "  Alice ", "age": "29", "score": None},
        {"name": "Bob",      "age": "NaN", "score": "88.5"},
        {"name": "  Alice ", "age": "29",  "score": None},   # duplicate
    ]

    cleaner = DataCleaner(raw)
    clean = (
        cleaner
        .strip_whitespace(fields=["name"])
        .fill_missing(value=0, fields=["score"])
        .coerce_types({"age": int, "score": float})
        .drop_duplicates()
        .get()
    )
"""

import copy
import re
from datetime import datetime
from typing import Any, Callable


class DataCleaner:
    """
    Fluent interface for cleaning a list-of-dict dataset.

    All mutating methods return ``self`` to support method chaining.

    Parameters
    ----------
    data:
        A list of ``dict`` rows to clean.  The input is *copied* so the
        original is never modified.
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data: list[dict[str, Any]] = copy.deepcopy(data)

    # ------------------------------------------------------------------
    # Missing-value handling
    # ------------------------------------------------------------------

    def drop_missing(self, fields: list[str] | None = None) -> "DataCleaner":
        """
        Remove rows that have ``None``, empty string, or ``"NaN"`` in
        any of *fields* (or any field if *fields* is ``None``).
        """
        def _is_missing(v: Any) -> bool:
            if v is None:
                return True
            if isinstance(v, float) and v != v:  # NaN check
                return True
            if isinstance(v, str) and v.strip().upper() in ("", "NAN", "NULL", "NONE", "N/A"):
                return True
            return False

        if fields is None:
            self._data = [
                row for row in self._data
                if not any(_is_missing(v) for v in row.values())
            ]
        else:
            self._data = [
                row for row in self._data
                if not any(_is_missing(row.get(f)) for f in fields)
            ]
        return self

    def fill_missing(
        self,
        value: Any,
        fields: list[str] | None = None,
    ) -> "DataCleaner":
        """
        Replace missing values (``None`` / ``"NaN"``/ empty string) with
        *value* in *fields* (or all fields if ``None``).
        """
        def _is_missing(v: Any) -> bool:
            if v is None:
                return True
            if isinstance(v, float) and v != v:
                return True
            if isinstance(v, str) and v.strip().upper() in ("", "NAN", "NULL", "NONE", "N/A"):
                return True
            return False

        for row in self._data:
            target_fields = fields if fields is not None else list(row.keys())
            for f in target_fields:
                if f in row and _is_missing(row[f]):
                    row[f] = value
        return self

    def flag_missing(
        self,
        flag_field: str = "_has_missing",
        fields: list[str] | None = None,
    ) -> "DataCleaner":
        """
        Add a boolean field *flag_field* indicating whether the row has
        any missing values in *fields* (or any field).
        """
        def _is_missing(v: Any) -> bool:
            return v is None or (isinstance(v, str) and v.strip() == "")

        for row in self._data:
            target = fields if fields is not None else list(row.keys())
            row[flag_field] = any(_is_missing(row.get(f)) for f in target)
        return self

    # ------------------------------------------------------------------
    # Duplicate handling
    # ------------------------------------------------------------------

    def drop_duplicates(self, fields: list[str] | None = None) -> "DataCleaner":
        """
        Remove duplicate rows, optionally comparing only *fields*.

        When *fields* is ``None``, a row is considered a duplicate if all
        field values match a previously seen row.
        """
        seen: list[dict[str, Any]] = []
        unique: list[dict[str, Any]] = []
        for row in self._data:
            key = {f: row.get(f) for f in (fields or list(row.keys()))}
            if key not in seen:
                seen.append(key)
                unique.append(row)
        self._data = unique
        return self

    # ------------------------------------------------------------------
    # String normalisation
    # ------------------------------------------------------------------

    def strip_whitespace(self, fields: list[str] | None = None) -> "DataCleaner":
        """Strip leading/trailing whitespace from string values."""
        for row in self._data:
            target = fields if fields is not None else list(row.keys())
            for f in target:
                if isinstance(row.get(f), str):
                    row[f] = row[f].strip()
        return self

    def normalise_case(
        self,
        mode: str = "lower",
        fields: list[str] | None = None,
    ) -> "DataCleaner":
        """
        Normalise string case.

        Parameters
        ----------
        mode:
            One of ``"lower"``, ``"upper"``, or ``"title"``.
        fields:
            Fields to normalise; defaults to all string fields.
        """
        ops = {"lower": str.lower, "upper": str.upper, "title": str.title}
        op = ops.get(mode, str.lower)
        for row in self._data:
            target = fields if fields is not None else list(row.keys())
            for f in target:
                if isinstance(row.get(f), str):
                    row[f] = op(row[f])
        return self

    def remove_special_characters(
        self,
        fields: list[str] | None = None,
        pattern: str = r"[^\w\s]",
        replacement: str = "",
    ) -> "DataCleaner":
        """Remove characters matching *pattern* from string fields."""
        for row in self._data:
            target = fields if fields is not None else list(row.keys())
            for f in target:
                if isinstance(row.get(f), str):
                    row[f] = re.sub(pattern, replacement, row[f])
        return self

    # ------------------------------------------------------------------
    # Type coercion
    # ------------------------------------------------------------------

    def coerce_types(
        self,
        type_map: dict[str, type | Callable],
        on_error: str = "null",
    ) -> "DataCleaner":
        """
        Coerce field values to specified Python types.

        Parameters
        ----------
        type_map:
            Mapping of field name → target type or callable.  Supported
            shortcuts: ``int``, ``float``, ``str``, ``bool``,
            ``datetime`` (parses ISO-8601 strings).
        on_error:
            What to do when coercion fails.  ``"null"`` sets the value to
            ``None``; ``"raise"`` re-raises the exception.
        """
        for row in self._data:
            for field, target_type in type_map.items():
                if field not in row:
                    continue
                val = row[field]
                if val is None:
                    continue
                try:
                    if target_type is bool:
                        row[field] = _coerce_bool(val)
                    elif target_type is datetime:
                        row[field] = _coerce_datetime(val)
                    else:
                        row[field] = target_type(val)
                except (ValueError, TypeError):
                    if on_error == "raise":
                        raise
                    row[field] = None
        return self

    # ------------------------------------------------------------------
    # Range / value constraints
    # ------------------------------------------------------------------

    def clamp(
        self,
        field: str,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> "DataCleaner":
        """Clamp numeric values in *field* to [*min_val*, *max_val*]."""
        for row in self._data:
            val = row.get(field)
            if val is None:
                continue
            try:
                val = float(val)
                if min_val is not None:
                    val = max(min_val, val)
                if max_val is not None:
                    val = min(max_val, val)
                row[field] = val
            except (TypeError, ValueError):
                pass
        return self

    def drop_out_of_range(
        self,
        field: str,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> "DataCleaner":
        """Remove rows where *field* is outside [*min_val*, *max_val*]."""
        def _in_range(val: Any) -> bool:
            try:
                v = float(val)
                if min_val is not None and v < min_val:
                    return False
                if max_val is not None and v > max_val:
                    return False
                return True
            except (TypeError, ValueError):
                return False

        self._data = [r for r in self._data if _in_range(r.get(field))]
        return self

    # ------------------------------------------------------------------
    # Field management
    # ------------------------------------------------------------------

    def rename_fields(self, mapping: dict[str, str]) -> "DataCleaner":
        """Rename fields according to *mapping* ``{old_name: new_name}``."""
        for row in self._data:
            for old, new in mapping.items():
                if old in row:
                    row[new] = row.pop(old)
        return self

    def drop_fields(self, fields: list[str]) -> "DataCleaner":
        """Remove the specified fields from every row."""
        for row in self._data:
            for f in fields:
                row.pop(f, None)
        return self

    def keep_fields(self, fields: list[str]) -> "DataCleaner":
        """Retain only the specified fields in every row."""
        self._data = [{f: row[f] for f in fields if f in row} for row in self._data]
        return self

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def get(self) -> list[dict[str, Any]]:
        """Return the cleaned dataset as a list of dicts."""
        return self._data

    def count(self) -> int:
        """Return the number of rows remaining after cleaning."""
        return len(self._data)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _coerce_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "y", "on")
    return bool(val)


def _coerce_datetime(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ):
            try:
                return datetime.strptime(val.strip(), fmt)
            except ValueError:
                continue
    raise ValueError(f"Cannot parse datetime from {val!r}")
