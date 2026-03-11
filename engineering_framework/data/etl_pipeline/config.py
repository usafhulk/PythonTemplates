"""ETL Pipeline Configuration."""
from dataclasses import dataclass


@dataclass
class ETLSettings:
    batch_size: int = 1000
    error_threshold: float = 0.05
    parallelism: int = 1
    checkpoint_enabled: bool = False
