"""Test Harness Configuration."""
from dataclasses import dataclass


@dataclass
class TestHarnessSettings:
    parallel: bool = False
    timeout_seconds: float = 30.0
    retry_failed: int = 0
    output_format: str = "text"
