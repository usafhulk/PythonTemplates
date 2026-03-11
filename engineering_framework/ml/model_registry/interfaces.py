"""Model Registry Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ModelStage(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelVersion:
    model_name: str
    version: str
    stage: ModelStage
    artifact_path: str
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


class ModelRegistry(ABC):
    @abstractmethod
    def register(self, model: ModelVersion) -> None: ...

    @abstractmethod
    def get_latest(self, model_name: str, stage: Optional[ModelStage] = None) -> Optional[ModelVersion]: ...

    @abstractmethod
    def list_versions(self, model_name: str) -> List[ModelVersion]: ...

    @abstractmethod
    def transition(self, model_name: str, version: str, new_stage: ModelStage) -> None: ...
