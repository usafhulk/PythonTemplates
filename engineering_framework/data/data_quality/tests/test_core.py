"""Data Quality Tests."""
import pytest
from ..core import NullRateCheck, UniquenessCheck, DataQualityMonitor


def test_null_rate_check_passes():
    check = NullRateCheck("name", max_null_rate=0.1)
    records = [{"name": "Alice"}, {"name": "Bob"}, {"name": None}]
    metric = check.compute(records)
    assert metric.value == pytest.approx(1/3, rel=0.01)
    assert metric.passed is False


def test_uniqueness_check():
    check = UniquenessCheck("id", min_uniqueness=1.0)
    records = [{"id": 1}, {"id": 2}, {"id": 3}]
    metric = check.compute(records)
    assert metric.value == 1.0
    assert metric.passed is True


def test_quality_monitor_overall():
    monitor = DataQualityMonitor()
    monitor.add_check(NullRateCheck("name", max_null_rate=0.0))
    records = [{"name": None}]
    report = monitor.run("test_dataset", records)
    assert report.overall_passed is False


def test_empty_dataset():
    check = NullRateCheck("col", max_null_rate=0.05)
    metric = check.compute([])
    assert metric.value == 0.0
    assert metric.passed is True
