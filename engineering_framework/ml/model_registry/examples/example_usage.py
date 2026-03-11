"""Model Registry Example."""
from engineering_framework.ml.model_registry.core import InMemoryModelRegistry
from engineering_framework.ml.model_registry.interfaces import ModelStage, ModelVersion

registry = InMemoryModelRegistry()
model_v1 = ModelVersion(
    model_name="fraud_detector",
    version="1.0.0",
    stage=ModelStage.DEVELOPMENT,
    artifact_path="/models/fraud_detector/1.0.0",
    metrics={"accuracy": 0.94, "f1": 0.91},
)
registry.register(model_v1)
registry.transition("fraud_detector", "1.0.0", ModelStage.PRODUCTION)
latest_prod = registry.get_latest("fraud_detector", stage=ModelStage.PRODUCTION)
print(f"Production model: {latest_prod.model_name} v{latest_prod.version}")
