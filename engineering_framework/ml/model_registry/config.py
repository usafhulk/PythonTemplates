"""Model Registry Configuration."""
from dataclasses import dataclass


@dataclass
class ModelRegistrySettings:
    backend: str = "inmemory"
    mlflow_tracking_uri: str = "http://localhost:5000"
    default_stage: str = "development"
    auto_archive_old: bool = True
