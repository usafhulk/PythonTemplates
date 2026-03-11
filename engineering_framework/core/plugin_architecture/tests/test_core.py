"""Plugin Architecture Tests."""
import pytest
from ..core import DefaultPluginRegistry, PluginBase


class SamplePlugin(PluginBase):
    _name = "sample"
    _version = "1.0.0"


def test_register_and_get():
    registry = DefaultPluginRegistry()
    plugin = SamplePlugin()
    registry.register(plugin)
    assert registry.get("sample") is plugin


def test_list_plugins():
    registry = DefaultPluginRegistry()
    registry.register(SamplePlugin())
    assert "sample" in registry.list_plugins()


def test_initialize_all():
    registry = DefaultPluginRegistry()
    registry.register(SamplePlugin())
    registry.initialize_all({"env": "test"})


def test_shutdown_all():
    registry = DefaultPluginRegistry()
    registry.register(SamplePlugin())
    registry.initialize_all({})
    registry.shutdown_all()
