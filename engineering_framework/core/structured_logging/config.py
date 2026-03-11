"""Structured Logging Configuration."""
from dataclasses import dataclass


@dataclass
class LoggingSettings:
    level: str = "INFO"
    format: str = "json"
    output: str = "stdout"
    include_timestamp: bool = True
