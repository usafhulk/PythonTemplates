"""Feature Store Core."""
import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .interfaces import Feature, FeatureGroup, FeatureStore

logger = logging.getLogger(__name__)


class InMemoryFeatureStore(FeatureStore):
    """In-memory feature store (production: Feast, Tecton)."""

    def __init__(self) -> None:
        self._features: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._groups: Dict[str, FeatureGroup] = {}
        self._timestamps: Dict[str, Dict[str, float]] = defaultdict(dict)

    def register_feature_group(self, group: FeatureGroup) -> None:
        self._groups[group.name] = group
        logger.info("Feature group registered: %s", group.name)

    def write_features(self, entity_id: str, feature_group: str, features: Dict[str, Any]) -> None:
        now = time.time()
        for name, value in features.items():
            key = f"{feature_group}.{name}"
            self._features[entity_id][key] = value
            self._timestamps[entity_id][key] = now
        logger.debug("Features written for entity %s: %d features", entity_id, len(features))

    def get_features(self, entity_id: str, feature_names: List[str]) -> Dict[str, Any]:
        entity_features = self._features.get(entity_id, {})
        result = {}
        for name in feature_names:
            result[name] = entity_features.get(name)
        return result

    def get_feature_vector(self, entity_id: str, feature_group: str) -> Dict[str, Any]:
        """Get all features for an entity in a group."""
        prefix = f"{feature_group}."
        return {
            k[len(prefix):]: v
            for k, v in self._features.get(entity_id, {}).items()
            if k.startswith(prefix)
        }
