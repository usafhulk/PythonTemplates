"""Model Service Tests."""
import pytest
from ..core import MockModelService
from ..interfaces import PredictionRequest


def test_mock_prediction():
    service = MockModelService(prediction_fn=lambda x: {"label": "cat", "score": 0.95})
    req = PredictionRequest(inputs={"image": "data"})
    resp = service.predict(req)
    assert resp.predictions["label"] == "cat"
    assert resp.model_name == "mock_model"


def test_health_check():
    service = MockModelService()
    assert service.health_check() is True


def test_stats_tracking():
    service = MockModelService()
    for _ in range(3):
        service.predict(PredictionRequest(inputs={}))
    stats = service.get_stats()
    assert stats["predictions"] == 3
    assert stats["errors"] == 0
    assert "avg_latency_seconds" in stats
