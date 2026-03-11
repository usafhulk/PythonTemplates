"""Model Registry Tests."""
import pytest
from ..core import InMemoryModelRegistry
from ..interfaces import ModelStage, ModelVersion


def make_model(name: str, version: str, stage: ModelStage = ModelStage.DEVELOPMENT) -> ModelVersion:
    return ModelVersion(model_name=name, version=version, stage=stage,
                        artifact_path=f"/models/{name}/{version}")


def test_register_and_get_latest():
    registry = InMemoryModelRegistry()
    model = make_model("classifier", "1.0.0")
    registry.register(model)
    latest = registry.get_latest("classifier")
    assert latest is not None
    assert latest.version == "1.0.0"


def test_list_versions():
    registry = InMemoryModelRegistry()
    registry.register(make_model("model", "1.0.0"))
    registry.register(make_model("model", "1.1.0"))
    versions = registry.list_versions("model")
    assert len(versions) == 2


def test_transition_stage():
    registry = InMemoryModelRegistry()
    registry.register(make_model("clf", "1.0.0"))
    registry.transition("clf", "1.0.0", ModelStage.PRODUCTION)
    latest = registry.get_latest("clf", stage=ModelStage.PRODUCTION)
    assert latest is not None


def test_get_latest_by_stage():
    registry = InMemoryModelRegistry()
    registry.register(make_model("m", "1.0.0", ModelStage.STAGING))
    registry.register(make_model("m", "2.0.0", ModelStage.PRODUCTION))
    prod = registry.get_latest("m", stage=ModelStage.PRODUCTION)
    assert prod.version == "2.0.0"
