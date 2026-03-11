"""Secrets Manager Tests."""
import os
import pytest
from ..core import InMemorySecretsManager, EnvSecretsManager


def test_set_and_get_secret():
    mgr = InMemorySecretsManager()
    mgr.set_secret("db_password", "super_secret")
    assert mgr.get_secret("db_password") == "super_secret"


def test_missing_secret_returns_none():
    mgr = InMemorySecretsManager()
    assert mgr.get_secret("nonexistent") is None


def test_delete_secret():
    mgr = InMemorySecretsManager()
    mgr.set_secret("key", "value")
    mgr.delete_secret("key")
    assert mgr.get_secret("key") is None


def test_list_secrets():
    mgr = InMemorySecretsManager()
    mgr.set_secret("api_key", "abc")
    mgr.set_secret("db_pass", "xyz")
    secrets = mgr.list_secrets()
    assert "api_key" in secrets
    assert "db_pass" in secrets


def test_env_secrets_manager():
    mgr = EnvSecretsManager(prefix="TEST_SECRETS")
    mgr.set_secret("api_key", "test_value")
    assert mgr.get_secret("api_key") == "test_value"
    mgr.delete_secret("api_key")
