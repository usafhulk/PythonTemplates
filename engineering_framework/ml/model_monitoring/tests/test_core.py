"""Model Monitoring Tests."""
import pytest
from ..core import InMemoryModelMonitor


def test_record_and_report():
    monitor = InMemoryModelMonitor()
    for _ in range(10):
        monitor.record_prediction("clf", prediction=1, ground_truth=1)
    report = monitor.get_report("clf")
    assert report.total_predictions == 10
    assert report.healthy is True


def test_high_error_rate_alert():
    monitor = InMemoryModelMonitor(error_rate_threshold=0.1)
    monitor.record_prediction("clf", prediction=1, ground_truth=0)
    monitor.record_prediction("clf", prediction=1, ground_truth=0)
    monitor.record_prediction("clf", prediction=1, ground_truth=1)
    report = monitor.get_report("clf")
    assert len(report.alerts) > 0
    assert not report.healthy


def test_empty_model():
    monitor = InMemoryModelMonitor()
    report = monitor.get_report("new_model")
    assert report.total_predictions == 0
    assert report.healthy is True
