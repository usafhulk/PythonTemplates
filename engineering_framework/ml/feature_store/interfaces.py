"""Feature Store Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Feature:
    name: str
    value: Any
    entity_id: str
    feature_group: str
    timestamp: Optional[float] = None


@dataclass
class FeatureGroup:
    name: str
    features: List[str] = field(default_factory=list)
    description: str = ""


class FeatureStore(ABC):
    @abstractmethod
    def write_features(self, entity_id: str, feature_group: str, features: Dict[str, Any]) -> None: ...

    @abstractmethod
    def get_features(self, entity_id: str, feature_names: List[str]) -> Dict[str, Any]: ...

    @abstractmethod
    def register_feature_group(self, group: FeatureGroup) -> None: ...
