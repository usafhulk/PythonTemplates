"""
data_analyzer.py
================
Descriptive statistics, correlation analysis, and distribution profiling
for list-of-dict datasets.

All computation uses the standard library (``statistics`` module) so there
are no third-party dependencies.  If ``pandas`` is available it can be used
optionally via ``DataAnalyzer.to_dataframe()``.

Usage::

    from wingbrace.data_analytics import DataAnalyzer

    data = [
        {"age": 25, "salary": 50000, "dept": "Engineering"},
        {"age": 30, "salary": 72000, "dept": "Engineering"},
        {"age": 28, "salary": 58000, "dept": "Marketing"},
        ...
    ]

    analyzer = DataAnalyzer(data)
    profile = analyzer.profile()
    print(profile["age"])
    # {'count': 3, 'mean': 27.67, 'median': 28.0, 'min': 25, 'max': 30, ...}

    corr = analyzer.correlation("age", "salary")
    print(f"Pearson r = {corr:.3f}")
"""

import math
import statistics
from collections import Counter
from typing import Any


class FieldProfile:
    """Statistical profile for a single dataset field."""

    def __init__(self, field: str, values: list[Any]) -> None:
        self.field = field
        self.total_count = len(values)
        self.null_count = sum(1 for v in values if v is None)
        self.non_null_values = [v for v in values if v is not None]

        # Numeric stats
        self._numeric: list[float] = []
        for v in self.non_null_values:
            try:
                self._numeric.append(float(v))
            except (TypeError, ValueError):
                pass

        # String stats
        self._strings: list[str] = [
            v for v in self.non_null_values if isinstance(v, str)
        ]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dtype(self) -> str:
        """Inferred data type: ``"numeric"``, ``"string"``, or ``"mixed"``."""
        if len(self._numeric) == len(self.non_null_values):
            return "numeric"
        if len(self._strings) == len(self.non_null_values):
            return "string"
        return "mixed"

    @property
    def non_null_count(self) -> int:
        return len(self.non_null_values)

    @property
    def null_rate(self) -> float:
        return self.null_count / self.total_count if self.total_count else 0.0

    @property
    def unique_count(self) -> int:
        try:
            return len(set(self.non_null_values))
        except TypeError:
            return len({str(v) for v in self.non_null_values})

    @property
    def mean(self) -> float | None:
        return statistics.mean(self._numeric) if self._numeric else None

    @property
    def median(self) -> float | None:
        return statistics.median(self._numeric) if self._numeric else None

    @property
    def mode(self) -> Any:
        try:
            return statistics.mode(self.non_null_values) if self.non_null_values else None
        except statistics.StatisticsError:
            return None

    @property
    def stdev(self) -> float | None:
        return statistics.stdev(self._numeric) if len(self._numeric) > 1 else None

    @property
    def variance(self) -> float | None:
        return statistics.variance(self._numeric) if len(self._numeric) > 1 else None

    @property
    def min(self) -> float | None:
        return min(self._numeric) if self._numeric else None

    @property
    def max(self) -> float | None:
        return max(self._numeric) if self._numeric else None

    def percentile(self, pct: float) -> float | None:
        """Return the *pct*-th percentile (0–100)."""
        if not self._numeric:
            return None
        sorted_v = sorted(self._numeric)
        idx = int(len(sorted_v) * pct / 100)
        return sorted_v[min(idx, len(sorted_v) - 1)]

    @property
    def q1(self) -> float | None:
        return self.percentile(25)

    @property
    def q3(self) -> float | None:
        return self.percentile(75)

    @property
    def iqr(self) -> float | None:
        q1, q3 = self.q1, self.q3
        return (q3 - q1) if (q1 is not None and q3 is not None) else None

    @property
    def value_counts(self) -> dict[Any, int]:
        """Frequency count of each distinct value."""
        return dict(Counter(self.non_null_values).most_common())

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        d: dict[str, Any] = {
            "field": self.field,
            "dtype": self.dtype,
            "total_count": self.total_count,
            "non_null_count": self.non_null_count,
            "null_count": self.null_count,
            "null_rate": round(self.null_rate, 4),
            "unique_count": self.unique_count,
        }
        if self._numeric:
            d.update(
                {
                    "mean": round(self.mean, 4) if self.mean is not None else None,
                    "median": self.median,
                    "stdev": round(self.stdev, 4) if self.stdev is not None else None,
                    "min": self.min,
                    "max": self.max,
                    "q1": self.q1,
                    "q3": self.q3,
                    "iqr": round(self.iqr, 4) if self.iqr is not None else None,
                    "p5": self.percentile(5),
                    "p95": self.percentile(95),
                }
            )
        if self.dtype == "string":
            d["mode"] = self.mode
            d["avg_length"] = (
                round(statistics.mean(len(s) for s in self._strings), 2)
                if self._strings
                else None
            )
        return d


class DataAnalyzer:
    """
    Profile and analyse a list-of-dict dataset.

    Parameters
    ----------
    data:
        The dataset to analyse.
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data = data

    # ------------------------------------------------------------------
    # Profiling
    # ------------------------------------------------------------------

    def profile(
        self, fields: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """
        Compute a statistical profile for every field (or the specified
        subset).

        Returns
        -------
        dict
            ``{field_name: profile_dict}``
        """
        if not self._data:
            return {}

        all_fields = fields or list(self._data[0].keys())
        return {
            f: FieldProfile(f, [row.get(f) for row in self._data]).to_dict()
            for f in all_fields
        }

    def field_profile(self, field: str) -> FieldProfile:
        """Return a ``FieldProfile`` object for a single *field*."""
        return FieldProfile(field, [row.get(field) for row in self._data])

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------

    def correlation(self, field_a: str, field_b: str) -> float | None:
        """
        Compute the Pearson correlation coefficient between two numeric fields.

        Returns ``None`` if insufficient data.
        """
        pairs = [
            (row.get(field_a), row.get(field_b))
            for row in self._data
            if row.get(field_a) is not None and row.get(field_b) is not None
        ]
        if len(pairs) < 2:
            return None

        try:
            xs = [float(a) for a, _ in pairs]
            ys = [float(b) for _, b in pairs]
        except (TypeError, ValueError):
            return None

        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / n
        std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs) / n)
        std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys) / n)

        if std_x == 0 or std_y == 0:
            return None
        return cov / (std_x * std_y)

    def correlation_matrix(
        self, fields: list[str] | None = None
    ) -> dict[str, dict[str, float | None]]:
        """
        Compute Pearson correlations for all pairs of numeric *fields*.

        Returns
        -------
        dict
            ``{field_a: {field_b: correlation_value}}``
        """
        numeric_fields = fields or self._numeric_fields()
        matrix: dict[str, dict[str, float | None]] = {}
        for fa in numeric_fields:
            matrix[fa] = {}
            for fb in numeric_fields:
                if fa == fb:
                    matrix[fa][fb] = 1.0
                else:
                    matrix[fa][fb] = self.correlation(fa, fb)
        return matrix

    # ------------------------------------------------------------------
    # Group-by / aggregation
    # ------------------------------------------------------------------

    def group_by(
        self,
        group_field: str,
        agg_field: str,
        func: str = "mean",
    ) -> dict[Any, float | None]:
        """
        Group rows by *group_field* and aggregate *agg_field*.

        Parameters
        ----------
        group_field:
            Categorical field to group on.
        agg_field:
            Numeric field to aggregate.
        func:
            Aggregation function: ``"mean"``, ``"sum"``, ``"min"``,
            ``"max"``, ``"count"``, ``"median"``.

        Returns
        -------
        dict
            ``{group_value: aggregated_value}``
        """
        groups: dict[Any, list[float]] = {}
        for row in self._data:
            key = row.get(group_field)
            val = row.get(agg_field)
            if val is not None:
                try:
                    groups.setdefault(key, []).append(float(val))
                except (TypeError, ValueError):
                    pass

        ops = {
            "mean": statistics.mean,
            "sum": sum,
            "min": min,
            "max": max,
            "count": len,
            "median": statistics.median,
        }
        agg_fn = ops.get(func, statistics.mean)
        return {
            k: round(agg_fn(vs), 4) if vs else None
            for k, vs in groups.items()
        }

    # ------------------------------------------------------------------
    # Frequency / distribution
    # ------------------------------------------------------------------

    def frequency_table(
        self, field: str, top_n: int | None = None
    ) -> dict[Any, dict[str, Any]]:
        """
        Return a frequency table for *field*.

        Returns
        -------
        dict
            ``{value: {"count": int, "pct": float}}``
        """
        values = [row.get(field) for row in self._data if row.get(field) is not None]
        total = len(values)
        counter = Counter(values)
        items = counter.most_common(top_n)
        return {
            v: {"count": c, "pct": round(c / total * 100, 2) if total else 0.0}
            for v, c in items
        }

    def histogram(
        self, field: str, bins: int = 10
    ) -> list[dict[str, Any]]:
        """
        Compute a histogram for a numeric *field*.

        Returns
        -------
        list of dict
            Each dict: ``{"bin_start": float, "bin_end": float, "count": int}``
        """
        values = []
        for row in self._data:
            v = row.get(field)
            if v is not None:
                try:
                    values.append(float(v))
                except (TypeError, ValueError):
                    pass
        if not values:
            return []

        v_min, v_max = min(values), max(values)
        if v_min == v_max:
            return [{"bin_start": v_min, "bin_end": v_max, "count": len(values)}]

        bin_width = (v_max - v_min) / bins
        buckets = [0] * bins
        for v in values:
            idx = int((v - v_min) / bin_width)
            idx = min(idx, bins - 1)
            buckets[idx] += 1

        return [
            {
                "bin_start": round(v_min + i * bin_width, 4),
                "bin_end": round(v_min + (i + 1) * bin_width, 4),
                "count": buckets[i],
            }
            for i in range(bins)
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _numeric_fields(self) -> list[str]:
        """Return field names whose values are predominantly numeric."""
        if not self._data:
            return []
        numeric = []
        for f in self._data[0].keys():
            numeric_count = 0
            for row in self._data[:100]:  # sample up to 100 rows
                v = row.get(f)
                if v is None:
                    continue
                try:
                    float(v)
                    numeric_count += 1
                except (TypeError, ValueError):
                    pass
            if numeric_count > 0:
                numeric.append(f)
        return numeric

    def summary(self) -> str:
        """Return a quick text summary of the dataset."""
        if not self._data:
            return "DataAnalyzer: empty dataset."
        fields = list(self._data[0].keys())
        return (
            f"DataAnalyzer: {len(self._data)} rows × {len(fields)} fields\n"
            f"Fields: {', '.join(fields)}"
        )
