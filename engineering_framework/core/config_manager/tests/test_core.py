"""Config Manager Tests."""
import os
import json
import tempfile
import pytest
from ..core import DefaultConfigManager, EnvConfigSource, FileConfigSource


def test_env_config_source_get():
    os.environ["TEST_FOO"] = "bar"
    source = EnvConfigSource(prefix="TEST")
    assert source.get("foo") == "bar"
    del os.environ["TEST_FOO"]


def test_file_config_source_get():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"key": "value"}, f)
        fname = f.name
    source = FileConfigSource(fname)
    assert source.get("key") == "value"


def test_default_config_manager_layering():
    mgr = DefaultConfigManager()
    os.environ["APP_DB_HOST"] = "localhost"
    mgr.add_source(EnvConfigSource(prefix="APP"))
    assert mgr.get("db_host") == "localhost"
    mgr.set("db_host", "remotehost")
    assert mgr.get("db_host") == "remotehost"
    del os.environ["APP_DB_HOST"]


def test_default_returns_fallback():
    mgr = DefaultConfigManager()
    assert mgr.get("nonexistent", "default_val") == "default_val"
