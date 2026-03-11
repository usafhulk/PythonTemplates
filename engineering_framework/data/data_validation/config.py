"""Data Validation Configuration."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DataValidationSettings:
    fail_fast: bool = False
    max_error_ratio: float = 0.01
    sample_size: Optional[int] = None
