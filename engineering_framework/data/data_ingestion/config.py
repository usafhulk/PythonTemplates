"""Data Ingestion Configuration."""
from dataclasses import dataclass


@dataclass
class IngestionSettings:
    batch_size: int = 5000
    dedup_enabled: bool = False
    schema_validation: bool = True
    error_threshold: float = 0.05
