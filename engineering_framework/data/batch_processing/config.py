"""Batch Processing Configuration."""
from dataclasses import dataclass


@dataclass
class BatchSettings:
    batch_size: int = 1000
    parallelism: int = 4
    retry_failed_batches: bool = True
    checkpoint_interval: int = 10
