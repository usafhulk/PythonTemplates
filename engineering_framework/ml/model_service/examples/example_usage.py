"""Model Service Example."""
from engineering_framework.ml.model_service.core import MockModelService
from engineering_framework.ml.model_service.interfaces import PredictionRequest

service = MockModelService(
    name="sentiment_model",
    prediction_fn=lambda x: {"sentiment": "positive", "confidence": 0.87}
)

req = PredictionRequest(inputs={"text": "I love this product!"})
resp = service.predict(req)
print(f"Prediction: {resp.predictions}")
print(f"Latency: {resp.metadata['latency_seconds']:.4f}s")
print(f"Stats: {service.get_stats()}")
