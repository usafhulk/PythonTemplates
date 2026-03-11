"""Service Layer Configuration."""
from dataclasses import dataclass


@dataclass
class ServiceSettings:
    pagination_default: int = 20
    pagination_max: int = 100
    cache_results: bool = False
