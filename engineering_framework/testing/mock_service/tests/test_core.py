"""Mock Service Tests."""
import pytest
from ..core import InMemoryMockService, AutoMock


def test_setup_and_call():
    mock = InMemoryMockService()
    mock.setup_response("get_user", {"id": 1, "name": "Alice"})
    result = mock.call("get_user", user_id=1)
    assert result == {"id": 1, "name": "Alice"}


def test_call_count():
    mock = InMemoryMockService()
    mock.setup_response("ping", "pong")
    mock.call("ping")
    mock.call("ping")
    assert mock.call_count("ping") == 2


def test_was_called_with():
    mock = InMemoryMockService()
    mock.setup_response("find", {"found": True})
    mock.call("find", "item_id", status="active")
    assert mock.was_called_with("find", "item_id", status="active")


def test_side_effect():
    mock = InMemoryMockService()
    mock.setup_side_effect("compute", lambda x: x * 2)
    result = mock.call("compute", 5)
    assert result == 10


def test_reset():
    mock = InMemoryMockService()
    mock.setup_response("method", "value")
    mock.call("method")
    mock.reset()
    assert mock.call_count("method") == 0
