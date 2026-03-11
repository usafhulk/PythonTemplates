"""Model Service Core."""
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from .interfaces import ModelService, PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class BaseModelService(ModelService):
    """Base model service with metrics and error handling."""

    def __init__(self, name: str, version: str = "1.0.0") -> None:
        self._name = name
        self._version = version
        self._prediction_count = 0
        self._error_count = 0
        self._total_latency = 0.0

    @property
    def model_name(self) -> str:
        return self._name

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        start = time.perf_counter()
        try:
            result = self._run_inference(request.inputs)
            latency = time.perf_counter() - start
            self._prediction_count += 1
            self._total_latency += latency
            logger.info("Prediction completed: model=%s, latency=%.3fs", self._name, latency)
            return PredictionResponse(
                predictions=result,
                model_name=self._name,
                model_version=self._version,
                metadata={"latency_seconds": latency},
            )
        except Exception as e:
            self._error_count += 1
            logger.error("Prediction error: %s", e)
            raise

    def _run_inference(self, inputs: Any) -> Any:
        raise NotImplementedError("Subclass must implement _run_inference")

    def health_check(self) -> bool:
        return True

    def get_stats(self) -> Dict[str, Any]:
        avg_latency = (self._total_latency / self._prediction_count
                       if self._prediction_count > 0 else 0.0)
        return {
            "model": self._name,
            "version": self._version,
            "predictions": self._prediction_count,
            "errors": self._error_count,
            "avg_latency_seconds": round(avg_latency, 4),
        }


class MockModelService(BaseModelService):
    """Mock model service for testing."""

    def __init__(self, name: str = "mock_model",
                 prediction_fn: Optional[Callable[[Any], Any]] = None) -> None:
        super().__init__(name)
        self._prediction_fn = prediction_fn or (lambda x: {"label": "default", "score": 0.9})

    def _run_inference(self, inputs: Any) -> Any:
        return self._prediction_fn(inputs)
