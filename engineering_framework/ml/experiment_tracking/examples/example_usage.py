"""Experiment Tracking Example."""
from engineering_framework.ml.experiment_tracking.core import InMemoryExperimentTracker

tracker = InMemoryExperimentTracker()

with tracker.run("model_training_v2") as run:
    tracker.log_param(run.run_id, "learning_rate", 0.001)
    tracker.log_param(run.run_id, "epochs", 10)
    tracker.log_param(run.run_id, "batch_size", 32)
    tracker.log_metric(run.run_id, "train_loss", 0.245)
    tracker.log_metric(run.run_id, "val_loss", 0.312)
    tracker.log_metric(run.run_id, "accuracy", 0.924)

completed = tracker.get_run(run.run_id)
print(f"Run: {completed.run_id[:8]}...")
print(f"Params: {completed.params}")
print(f"Metrics: {completed.metrics}")
print(f"Status: {completed.status}")
