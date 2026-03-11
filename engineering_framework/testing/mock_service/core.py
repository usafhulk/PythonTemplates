"""Mock Service Core."""
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from .interfaces import MockCall, MockService

logger = logging.getLogger(__name__)


class InMemoryMockService(MockService):
    """Configurable mock service for dependency injection in tests."""

    def __init__(self) -> None:
        self._responses: Dict[str, Any] = {}
        self._call_log: Dict[str, List[MockCall]] = defaultdict(list)
        self._side_effects: Dict[str, Callable] = {}

    def setup_response(self, method: str, return_value: Any) -> None:
        self._responses[method] = return_value

    def setup_side_effect(self, method: str, side_effect: Callable) -> None:
        self._side_effects[method] = side_effect

    def call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        if method in self._side_effects:
            result = self._side_effects[method](*args, **kwargs)
        else:
            result = self._responses.get(method)
        self._call_log[method].append(MockCall(method=method, args=args, kwargs=kwargs, return_value=result))
        return result

    def call_count(self, method: str) -> int:
        return len(self._call_log[method])

    def was_called_with(self, method: str, *args: Any, **kwargs: Any) -> bool:
        calls = self._call_log.get(method, [])
        return any(c.args == args and c.kwargs == kwargs for c in calls)

    def reset(self) -> None:
        self._call_log.clear()
        self._responses.clear()
        self._side_effects.clear()


def create_mock(spec: type) -> "AutoMock":
    """Create a mock from a class spec."""
    return AutoMock(spec)


class AutoMock:
    """Auto-generating mock for any class."""

    def __init__(self, spec: type) -> None:
        self._spec = spec
        self._service = InMemoryMockService()

    def __getattr__(self, name: str) -> Callable:
        def method_mock(*args: Any, **kwargs: Any) -> Any:
            return self._service.call(name, *args, **kwargs)
        return method_mock

    def setup(self, method: str, return_value: Any) -> None:
        self._service.setup_response(method, return_value)

    def call_count(self, method: str) -> int:
        return self._service.call_count(method)
