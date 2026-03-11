"""Dependency Injection Configuration."""
from dataclasses import dataclass


@dataclass
class DISettings:
    auto_wire: bool = True
    strict_mode: bool = False
