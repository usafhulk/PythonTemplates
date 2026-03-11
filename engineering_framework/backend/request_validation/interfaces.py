"""Request Validation Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)


class Validator(ABC):
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> ValidationResult: ...
