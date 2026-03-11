"""Environment Manager Tests."""
import os
import pytest
from ..core import DefaultEnvironmentManager
from ..interfaces import Environment


def test_default_environment():
    mgr = DefaultEnvironmentManager()
    mgr.set(Environment.DEVELOPMENT)
    assert mgr.is_development() is True


def test_production_detection():
    mgr = DefaultEnvironmentManager()
    mgr.set(Environment.PRODUCTION)
    assert mgr.is_production() is True
    assert mgr.is_development() is False


def test_env_from_env_var():
    os.environ["APP_ENV"] = "staging"
    mgr = DefaultEnvironmentManager()
    assert mgr.current() == Environment.STAGING
    del os.environ["APP_ENV"]
