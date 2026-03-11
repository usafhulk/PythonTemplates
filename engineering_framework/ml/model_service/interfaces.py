"""Model Service Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PredictionRequest:
    inputs: Any
    model_version: str = "latest"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResponse:
    predictions: Any
    model_name: str
    model_version: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelService(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def predict(self, request: PredictionRequest) -> PredictionResponse: ...

    @abstractmethod
    def health_check(self) -> bool: ...
