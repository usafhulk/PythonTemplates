"""
data_transformer.py
===================
Data transformation helpers for reshaping, normalising, and encoding
list-of-dict datasets.

Provides a fluent interface (method chaining) similar to ``DataCleaner``.

Features:
    - Min-max and Z-score normalisation of numeric fields
    - One-hot encoding for categorical fields
    - Label encoding for ordered categoricals
    - Binning / bucketing of continuous values
    - Date/time feature extraction (year, month, day, weekday, hour)
    - Flattening nested dicts
    - Adding computed / derived fields
    - Reordering and pivoting rows to columns

Usage::

    from wingbrace.data_cleanup import DataTransformer

    raw = [
        {"name": "Alice", "score": 75, "grade": "B", "joined": "2023-06-01"},
        {"name": "Bob",   "score": 90, "grade": "A", "joined": "2023-08-15"},
        {"name": "Carol", "score": 60, "grade": "C", "joined": "2023-01-20"},
    ]

    transformer = DataTransformer(raw)
    transformed = (
        transformer
        .normalise_minmax(fields=["score"])
        .one_hot_encode("grade", prefix="grade")
        .extract_date_parts("joined", parts=["year", "month", "day"])
        .drop_fields(["joined"])
        .get()
    )
"""

import copy
import math
from datetime import datetime
from typing import Any, Callable


class DataTransformer:
    """
    Fluent data transformation pipeline for list-of-dict datasets.

    Parameters
    ----------
    data:
        A list of ``dict`` rows to transform.  The input is *copied*.
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data: list[dict[str, Any]] = copy.deepcopy(data)

    # ------------------------------------------------------------------
    # Numeric normalisation
    # ------------------------------------------------------------------

    def normalise_minmax(
        self,
        fields: list[str],
        feature_range: tuple[float, float] = (0.0, 1.0),
    ) -> "DataTransformer":
        """
        Apply min-max scaling to *fields*, mapping values to
        [*feature_range[0]*, *feature_range[1]*].
        """
        lo, hi = feature_range
        for f in fields:
            values = [r[f] for r in self._data if r.get(f) is not None]
            if not values:
                continue
            v_min = min(values)
            v_max = max(values)
            span = v_max - v_min or 1.0  # avoid zero-division
            for row in self._data:
                if row.get(f) is not None:
                    row[f] = lo + (row[f] - v_min) / span * (hi - lo)
        return self

    def normalise_zscore(self, fields: list[str]) -> "DataTransformer":
        """
        Standardise *fields* to zero mean and unit variance (z-score).
        """
        for f in fields:
            values = [r[f] for r in self._data if r.get(f) is not None]
            if len(values) < 2:
                continue
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = math.sqrt(variance) or 1.0
            for row in self._data:
                if row.get(f) is not None:
                    row[f] = (row[f] - mean) / std
        return self

    def round_fields(
        self, fields: list[str], decimals: int = 4
    ) -> "DataTransformer":
        """Round numeric *fields* to *decimals* decimal places."""
        for row in self._data:
            for f in fields:
                if isinstance(row.get(f), float):
                    row[f] = round(row[f], decimals)
        return self

    # ------------------------------------------------------------------
    # Categorical encoding
    # ------------------------------------------------------------------

    def one_hot_encode(
        self,
        field: str,
        prefix: str | None = None,
        drop_original: bool = True,
    ) -> "DataTransformer":
        """
        Replace a categorical *field* with binary indicator columns.

        Parameters
        ----------
        field:
            Name of the categorical field.
        prefix:
            Prefix for generated column names.  Defaults to *field*.
        drop_original:
            Whether to remove the original *field* after encoding.
        """
        pfx = prefix or field
        categories = sorted(
            {str(row.get(field, "")) for row in self._data if row.get(field) is not None}
        )
        for row in self._data:
            val = str(row.get(field, ""))
            for cat in categories:
                row[f"{pfx}_{cat}"] = 1 if val == cat else 0
            if drop_original:
                row.pop(field, None)
        return self

    def label_encode(
        self,
        field: str,
        mapping: dict[Any, int] | None = None,
        new_field: str | None = None,
    ) -> "DataTransformer":
        """
        Replace a categorical *field* with integer labels.

        Parameters
        ----------
        field:
            Categorical field to encode.
        mapping:
            Optional explicit ``{value: label}`` dict.  If ``None``,
            labels are assigned alphabetically (0-based).
        new_field:
            Name for the encoded field.  Defaults to *field*.
        """
        target = new_field or field
        if mapping is None:
            categories = sorted(
                {row[field] for row in self._data if row.get(field) is not None}
            )
            mapping = {cat: idx for idx, cat in enumerate(categories)}
        for row in self._data:
            if field in row:
                row[target] = mapping.get(row[field], -1)
        return self

    # ------------------------------------------------------------------
    # Binning
    # ------------------------------------------------------------------

    def bin(
        self,
        field: str,
        bins: list[float],
        labels: list[str] | None = None,
        new_field: str | None = None,
    ) -> "DataTransformer":
        """
        Bucket a continuous numeric *field* into discrete bins.

        Parameters
        ----------
        field:
            Numeric field to bin.
        bins:
            Bin edge values, e.g. ``[0, 18, 65, 120]`` creates three bins:
            [0, 18), [18, 65), [65, 120].
        labels:
            Optional labels for each bin.  Must have ``len(bins) - 1``
            elements.
        new_field:
            Name for the binned field.  Defaults to ``field + "_bin"``.
        """
        target = new_field or f"{field}_bin"
        auto_labels = labels or [
            f"[{bins[i]},{bins[i+1]})" for i in range(len(bins) - 1)
        ]
        for row in self._data:
            val = row.get(field)
            if val is None:
                row[target] = None
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                row[target] = None
                continue
            assigned = None
            for i in range(len(bins) - 1):
                if bins[i] <= v < bins[i + 1]:
                    assigned = auto_labels[i]
                    break
            # include the right edge of the last bin
            if assigned is None and v == bins[-1]:
                assigned = auto_labels[-1]
            row[target] = assigned
        return self

    # ------------------------------------------------------------------
    # Date / time feature extraction
    # ------------------------------------------------------------------

    def extract_date_parts(
        self,
        field: str,
        parts: list[str] | None = None,
        drop_original: bool = False,
    ) -> "DataTransformer":
        """
        Extract date/time components from an ISO-8601 date string field.

        Parameters
        ----------
        field:
            Field containing date strings or ``datetime`` objects.
        parts:
            Subset of ``["year", "month", "day", "hour", "minute",
            "weekday", "quarter"]``.  Defaults to all.
        drop_original:
            Whether to remove the original *field* after extraction.
        """
        all_parts = ["year", "month", "day", "hour", "minute", "weekday", "quarter"]
        selected = parts or all_parts

        for row in self._data:
            val = row.get(field)
            if val is None:
                for p in selected:
                    row[f"{field}_{p}"] = None
                continue
            dt = _parse_datetime(val)
            if dt is None:
                for p in selected:
                    row[f"{field}_{p}"] = None
                continue
            for p in selected:
                if p == "year":
                    row[f"{field}_year"] = dt.year
                elif p == "month":
                    row[f"{field}_month"] = dt.month
                elif p == "day":
                    row[f"{field}_day"] = dt.day
                elif p == "hour":
                    row[f"{field}_hour"] = dt.hour
                elif p == "minute":
                    row[f"{field}_minute"] = dt.minute
                elif p == "weekday":
                    row[f"{field}_weekday"] = dt.weekday()  # 0=Monday
                elif p == "quarter":
                    row[f"{field}_quarter"] = (dt.month - 1) // 3 + 1
            if drop_original:
                row.pop(field, None)
        return self

    # ------------------------------------------------------------------
    # Structural transforms
    # ------------------------------------------------------------------

    def flatten(
        self, field: str, separator: str = "_", drop_original: bool = True
    ) -> "DataTransformer":
        """
        Flatten a nested dict *field* into top-level keys.

        Example: ``{"address": {"city": "Springfield"}}``
        becomes ``{"address_city": "Springfield"}``.
        """
        for row in self._data:
            nested = row.get(field)
            if isinstance(nested, dict):
                for k, v in nested.items():
                    row[f"{field}{separator}{k}"] = v
                if drop_original:
                    row.pop(field, None)
        return self

    def add_field(
        self,
        new_field: str,
        func: Callable[[dict[str, Any]], Any],
    ) -> "DataTransformer":
        """
        Add a derived field *new_field* computed from each row.

        Parameters
        ----------
        new_field:
            Name of the new field.
        func:
            Callable that receives the row dict and returns the new value.

        Example
        -------
        ::

            transformer.add_field("full_name",
                                  lambda r: f"{r['first']} {r['last']}")
        """
        for row in self._data:
            row[new_field] = func(row)
        return self

    def rename_fields(self, mapping: dict[str, str]) -> "DataTransformer":
        """Rename fields according to *mapping* ``{old: new}``."""
        for row in self._data:
            for old, new in mapping.items():
                if old in row:
                    row[new] = row.pop(old)
        return self

    def drop_fields(self, fields: list[str]) -> "DataTransformer":
        """Remove *fields* from every row."""
        for row in self._data:
            for f in fields:
                row.pop(f, None)
        return self

    def reorder_fields(self, order: list[str]) -> "DataTransformer":
        """
        Reorder dict keys so that *order* fields come first.
        Remaining fields keep their original relative order.
        """
        def _reorder(row: dict[str, Any]) -> dict[str, Any]:
            reordered: dict[str, Any] = {}
            for f in order:
                if f in row:
                    reordered[f] = row[f]
            for k, v in row.items():
                if k not in reordered:
                    reordered[k] = v
            return reordered

        self._data = [_reorder(row) for row in self._data]
        return self

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def get(self) -> list[dict[str, Any]]:
        """Return the transformed dataset."""
        return self._data

    def count(self) -> int:
        """Return the number of rows in the dataset."""
        return len(self._data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_datetime(val: Any) -> datetime | None:
    if isinstance(val, datetime):
        return val
    if not isinstance(val, str):
        return None
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
    return None
