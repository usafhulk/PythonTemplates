"""Request Validation Configuration."""
from dataclasses import dataclass


@dataclass
class ValidationSettings:
    strict_mode: bool = True
    collect_all_errors: bool = True
    max_body_size_bytes: int = 1_048_576
