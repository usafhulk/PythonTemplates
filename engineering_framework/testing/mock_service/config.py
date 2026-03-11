"""Mock Service Configuration."""
from dataclasses import dataclass
from typing import Any


@dataclass
class MockServiceSettings:
    strict_mode: bool = False
    record_calls: bool = True
    default_return: Any = None
