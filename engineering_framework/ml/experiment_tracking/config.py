"""Experiment Tracking Configuration."""
from dataclasses import dataclass


@dataclass
class ExperimentTrackingSettings:
    backend: str = "inmemory"
    mlflow_uri: str = "http://localhost:5000"
    auto_log: bool = True
    artifact_store: str = "/tmp/artifacts"
