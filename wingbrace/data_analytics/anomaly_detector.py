"""
anomaly_detector.py
===================
Outlier and anomaly detection algorithms for list-of-dict datasets.

Implements four classic detection methods using only the standard library:

- **Z-score**: flags values more than *n* standard deviations from the mean.
- **IQR (Tukey fences)**: flags values outside Q1−k·IQR … Q3+k·IQR.
- **Modified Z-score**: more robust version using the median absolute deviation.
- **Isolation score**: lightweight proxy inspired by Isolation Forest (no deps).

Usage::

    from wingbrace.data_analytics import AnomalyDetector

    data = [
        {"value": 10}, {"value": 11}, {"value": 12},
        {"value": 200},  # anomaly!
        {"value": 10}, {"value": 9},
    ]

    detector = AnomalyDetector(data)
    results = detector.zscore(field="value", threshold=3.0)

    for r in results.anomalies:
        print(r)
    # AnomalyRecord(row_index=3, field='value', value=200, method='zscore', score=14.6)
"""

import math
import statistics
from dataclasses import dataclass
from typing import Any


@dataclass
class AnomalyRecord:
    """Describes a single detected anomaly."""

    row_index: int
    field: str
    value: Any
    method: str
    score: float

    def __str__(self) -> str:
        return (
            f"AnomalyRecord(row={self.row_index}, field={self.field!r}, "
            f"value={self.value!r}, method={self.method}, score={self.score:.4f})"
        )


class AnomalyResult:
    """Aggregated result from an anomaly detection run."""

    def __init__(
        self,
        method: str,
        field: str,
        anomalies: list[AnomalyRecord],
        total_rows: int,
    ) -> None:
        self.method = method
        self.field = field
        self.anomalies = anomalies
        self.total_rows = total_rows

    @property
    def anomaly_count(self) -> int:
        return len(self.anomalies)

    @property
    def anomaly_rate(self) -> float:
        return self.anomaly_count / self.total_rows if self.total_rows else 0.0

    @property
    def anomaly_indices(self) -> list[int]:
        return [a.row_index for a in self.anomalies]

    def summary(self) -> str:
        return (
            f"AnomalyResult [{self.method}] field={self.field!r}: "
            f"{self.anomaly_count}/{self.total_rows} anomalies "
            f"({self.anomaly_rate:.2%})"
        )

    def __repr__(self) -> str:
        return self.summary()


class AnomalyDetector:
    """
    Detect anomalies in numeric fields of a list-of-dict dataset.

    Parameters
    ----------
    data:
        The dataset to inspect.
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data = data

    # ------------------------------------------------------------------
    # Z-score
    # ------------------------------------------------------------------

    def zscore(
        self,
        field: str,
        threshold: float = 3.0,
        add_score_field: bool = False,
    ) -> AnomalyResult:
        """
        Detect anomalies using the Z-score method.

        A data point is flagged as an anomaly when
        ``|z| = |(x - mean) / std| > threshold``.

        Parameters
        ----------
        field:
            Numeric field to analyse.
        threshold:
            Z-score threshold (default 3.0 — covers ~99.7% of a normal dist).
        add_score_field:
            When ``True``, add a ``{field}_zscore`` column to each row.
        """
        values = self._numeric_values(field)
        if len(values) < 2:
            return AnomalyResult("zscore", field, [], len(self._data))

        mean = statistics.mean(values)
        std = statistics.stdev(values)
        if std == 0:
            return AnomalyResult("zscore", field, [], len(self._data))

        anomalies: list[AnomalyRecord] = []
        for idx, row in enumerate(self._data):
            val = row.get(field)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            z = abs((v - mean) / std)
            if add_score_field:
                row[f"{field}_zscore"] = round(z, 4)
            if z > threshold:
                anomalies.append(
                    AnomalyRecord(idx, field, val, "zscore", round(z, 4))
                )
        return AnomalyResult("zscore", field, anomalies, len(self._data))

    # ------------------------------------------------------------------
    # IQR (Tukey fences)
    # ------------------------------------------------------------------

    def iqr(
        self,
        field: str,
        k: float = 1.5,
        add_fence_fields: bool = False,
    ) -> AnomalyResult:
        """
        Detect anomalies using the IQR (Tukey fence) method.

        A value is flagged when it falls outside
        ``[Q1 − k·IQR, Q3 + k·IQR]``.

        Parameters
        ----------
        field:
            Numeric field to analyse.
        k:
            Fence multiplier (1.5 = mild, 3.0 = extreme outliers).
        """
        values = self._numeric_values(field)
        if len(values) < 4:
            return AnomalyResult("iqr", field, [], len(self._data))

        q1 = self._percentile(values, 25)
        q3 = self._percentile(values, 75)
        iqr_val = q3 - q1
        lower = q1 - k * iqr_val
        upper = q3 + k * iqr_val

        if add_fence_fields:
            for row in self._data:
                row[f"{field}_iqr_lower"] = round(lower, 4)
                row[f"{field}_iqr_upper"] = round(upper, 4)

        anomalies: list[AnomalyRecord] = []
        for idx, row in enumerate(self._data):
            val = row.get(field)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            if v < lower or v > upper:
                score = max(abs(v - lower), abs(v - upper)) / (iqr_val or 1.0)
                anomalies.append(
                    AnomalyRecord(idx, field, val, "iqr", round(score, 4))
                )
        return AnomalyResult("iqr", field, anomalies, len(self._data))

    # ------------------------------------------------------------------
    # Modified Z-score (MAD-based)
    # ------------------------------------------------------------------

    def modified_zscore(
        self,
        field: str,
        threshold: float = 3.5,
    ) -> AnomalyResult:
        """
        Detect anomalies using the modified Z-score (Iglewicz & Hoaglin).

        Uses the Median Absolute Deviation (MAD) instead of the mean and
        standard deviation, making it more robust to existing outliers.

        ``modified_z = 0.6745 * |x - median| / MAD``

        Parameters
        ----------
        threshold:
            Threshold for the modified Z-score (default 3.5 per the
            original paper).
        """
        values = self._numeric_values(field)
        if len(values) < 3:
            return AnomalyResult("modified_zscore", field, [], len(self._data))

        med = statistics.median(values)
        deviations = [abs(v - med) for v in values]
        mad = statistics.median(deviations)
        if mad == 0:
            return AnomalyResult("modified_zscore", field, [], len(self._data))

        anomalies: list[AnomalyRecord] = []
        for idx, row in enumerate(self._data):
            val = row.get(field)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            mz = 0.6745 * abs(v - med) / mad
            if mz > threshold:
                anomalies.append(
                    AnomalyRecord(idx, field, val, "modified_zscore", round(mz, 4))
                )
        return AnomalyResult("modified_zscore", field, anomalies, len(self._data))

    # ------------------------------------------------------------------
    # Simple isolation score
    # ------------------------------------------------------------------

    def isolation_score(
        self,
        field: str,
        threshold: float = 0.6,
        num_samples: int = 50,
    ) -> AnomalyResult:
        """
        Compute a lightweight isolation score for each data point.

        Approximates the intuition behind Isolation Forest: anomalous
        values can be isolated with fewer random splits.  A pure Python
        implementation — no external dependencies.

        Parameters
        ----------
        field:
            Numeric field to score.
        threshold:
            Score above which a point is considered an anomaly (0–1).
        num_samples:
            Number of random isolation attempts per data point.
        """
        import random

        values = self._numeric_values(field)
        if len(values) < 4:
            return AnomalyResult("isolation_score", field, [], len(self._data))

        v_min, v_max = min(values), max(values)
        if v_min == v_max:
            return AnomalyResult("isolation_score", field, [], len(self._data))

        rng = random.Random(42)  # reproducible

        def _score(val: float) -> float:
            total_depth = 0.0
            for _ in range(num_samples):
                lo, hi = v_min, v_max
                depth = 0
                current_values = values[:]
                while len(current_values) > 1:
                    split = rng.uniform(lo, hi)
                    left = [v for v in current_values if v < split]
                    right = [v for v in current_values if v >= split]
                    if val < split:
                        current_values = left
                        hi = split
                    else:
                        current_values = right
                        lo = split
                    depth += 1
                    if depth > 30:
                        break
                total_depth += depth
            avg_depth = total_depth / num_samples
            # Normalise: shallower depth → higher anomaly score
            max_possible = math.log2(max(len(values), 2))
            return max(0.0, 1.0 - avg_depth / max_possible) if max_possible else 0.0

        anomalies: list[AnomalyRecord] = []
        for idx, row in enumerate(self._data):
            val = row.get(field)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            s = _score(v)
            if s > threshold:
                anomalies.append(
                    AnomalyRecord(idx, field, val, "isolation_score", round(s, 4))
                )
        return AnomalyResult("isolation_score", field, anomalies, len(self._data))

    # ------------------------------------------------------------------
    # Multi-field wrapper
    # ------------------------------------------------------------------

    def detect_all(
        self,
        fields: list[str],
        method: str = "zscore",
        **kwargs: Any,
    ) -> dict[str, AnomalyResult]:
        """
        Run *method* on each field in *fields*.

        Parameters
        ----------
        fields:
            Fields to analyse.
        method:
            One of ``"zscore"``, ``"iqr"``, ``"modified_zscore"``,
            ``"isolation_score"``.
        **kwargs:
            Additional keyword arguments forwarded to the detection method.

        Returns
        -------
        dict
            ``{field_name: AnomalyResult}``
        """
        method_map = {
            "zscore": self.zscore,
            "iqr": self.iqr,
            "modified_zscore": self.modified_zscore,
            "isolation_score": self.isolation_score,
        }
        fn = method_map.get(method)
        if fn is None:
            raise ValueError(
                f"Unknown method {method!r}. "
                f"Choose from: {list(method_map.keys())}"
            )
        return {f: fn(field=f, **kwargs) for f in fields}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _numeric_values(self, field: str) -> list[float]:
        out: list[float] = []
        for row in self._data:
            v = row.get(field)
            if v is None:
                continue
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                pass
        return out

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        sorted_v = sorted(values)
        idx = int(len(sorted_v) * pct / 100)
        return sorted_v[min(idx, len(sorted_v) - 1)]
