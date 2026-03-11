"""Model Service Configuration."""
from dataclasses import dataclass


@dataclass
class ModelServiceSettings:
    model_name: str = "default_model"
    model_version: str = "1.0.0"
    max_batch_size: int = 32
    timeout_seconds: float = 30.0
    cache_predictions: bool = False
