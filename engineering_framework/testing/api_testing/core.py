"""API Testing Core."""
import logging
from typing import Any, Callable, Dict, List, Optional

from .interfaces import APITestClient, APITestRequest, APITestResponse

logger = logging.getLogger(__name__)


class MockAPITestClient(APITestClient):
    """Mock API client for unit testing."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable] = {}
        self._call_log: List[APITestRequest] = []

    def register(self, method: str, path: str, handler: Callable) -> None:
        self._handlers[f"{method.upper()}:{path}"] = handler

    def send(self, request: APITestRequest) -> APITestResponse:
        self._call_log.append(request)
        key = f"{request.method.upper()}:{request.path}"
        handler = self._handlers.get(key)
        if handler:
            return handler(request)
        return APITestResponse(status_code=404, body={"error": "not found"})


class APITestAssertions:
    """Fluent assertion builder for API responses."""

    def __init__(self, response: APITestResponse) -> None:
        self._response = response
        self._errors: List[str] = []

    def status(self, expected: int) -> "APITestAssertions":
        if self._response.status_code != expected:
            self._errors.append(
                f"Expected status {expected}, got {self._response.status_code}"
            )
        return self

    def has_key(self, key: str) -> "APITestAssertions":
        if not isinstance(self._response.body, dict) or key not in self._response.body:
            self._errors.append(f"Response body missing key: '{key}'")
        return self

    def body_equals(self, expected: Any) -> "APITestAssertions":
        if self._response.body != expected:
            self._errors.append(f"Expected body {expected}, got {self._response.body}")
        return self

    def assert_all(self) -> None:
        if self._errors:
            raise AssertionError("API assertions failed:\n" + "\n".join(self._errors))

    @classmethod
    def from_response(cls, response: APITestResponse) -> "APITestAssertions":
        return cls(response)
