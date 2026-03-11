"""Model Registry Core."""
import logging
from typing import Dict, List, Optional

from .interfaces import ModelRegistry, ModelStage, ModelVersion

logger = logging.getLogger(__name__)


class InMemoryModelRegistry(ModelRegistry):
    """In-memory model registry (swap for MLflow)."""

    def __init__(self) -> None:
        self._models: Dict[str, List[ModelVersion]] = {}

    def register(self, model: ModelVersion) -> None:
        if model.model_name not in self._models:
            self._models[model.model_name] = []
        self._models[model.model_name].append(model)
        logger.info("Model registered: %s v%s (%s)", model.model_name, model.version, model.stage.value)

    def get_latest(self, model_name: str, stage: Optional[ModelStage] = None) -> Optional[ModelVersion]:
        versions = self._models.get(model_name, [])
        if stage:
            versions = [v for v in versions if v.stage == stage]
        return versions[-1] if versions else None

    def list_versions(self, model_name: str) -> List[ModelVersion]:
        return self._models.get(model_name, [])

    def transition(self, model_name: str, version: str, new_stage: ModelStage) -> None:
        for mv in self._models.get(model_name, []):
            if mv.version == version:
                old_stage = mv.stage
                mv.stage = new_stage
                logger.info("Model %s v%s transitioned: %s -> %s",
                           model_name, version, old_stage.value, new_stage.value)
                return
        raise ValueError(f"Model {model_name} v{version} not found")
