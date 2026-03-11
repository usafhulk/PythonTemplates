"""Config Service Tests."""
import pytest
from ..core import InMemoryConfigService


def test_set_and_get():
    svc = InMemoryConfigService({"debug": False})
    svc.set("debug", True)
    assert svc.get("debug") is True


def test_default_value():
    svc = InMemoryConfigService()
    assert svc.get("missing", "default") == "default"


def test_watcher_notified():
    svc = InMemoryConfigService()
    changes = []
    svc.watch("feature_x", lambda k, v: changes.append((k, v)))
    svc.set("feature_x", True)
    assert ("feature_x", True) in changes


def test_snapshot():
    svc = InMemoryConfigService({"a": 1, "b": 2})
    assert svc.snapshot() == {"a": 1, "b": 2}
