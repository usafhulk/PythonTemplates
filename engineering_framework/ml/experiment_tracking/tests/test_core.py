"""Experiment Tracking Tests."""
import pytest
from ..core import InMemoryExperimentTracker


def test_start_and_end_run():
    tracker = InMemoryExperimentTracker()
    run = tracker.start_run("test_experiment")
    assert run.status == "running"
    tracker.end_run(run.run_id)
    run = tracker.get_run(run.run_id)
    assert run.status == "completed"


def test_log_params_and_metrics():
    tracker = InMemoryExperimentTracker()
    run = tracker.start_run("exp")
    tracker.log_param(run.run_id, "learning_rate", 0.001)
    tracker.log_metric(run.run_id, "accuracy", 0.95)
    r = tracker.get_run(run.run_id)
    assert r.params["learning_rate"] == 0.001
    assert r.metrics["accuracy"] == 0.95


def test_context_manager():
    tracker = InMemoryExperimentTracker()
    with tracker.run("ml_experiment") as run:
        tracker.log_metric(run.run_id, "loss", 0.1)
    r = tracker.get_run(run.run_id)
    assert r.status == "completed"


def test_list_runs():
    tracker = InMemoryExperimentTracker()
    tracker.start_run("exp_a")
    tracker.start_run("exp_a")
    tracker.start_run("exp_b")
    runs = tracker.list_runs("exp_a")
    assert len(runs) == 2
