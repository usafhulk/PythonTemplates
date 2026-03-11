"""Feature Flags Tests."""
import pytest
from ..core import InMemoryFeatureFlagProvider, FeatureFlagManager


def test_flag_enabled():
    provider = InMemoryFeatureFlagProvider()
    provider.set_flag("new_ui", True)
    assert provider.is_enabled("new_ui") is True


def test_flag_disabled_by_default():
    provider = InMemoryFeatureFlagProvider()
    assert provider.is_enabled("unknown_flag") is False


def test_rule_based_flag():
    provider = InMemoryFeatureFlagProvider()
    provider.add_rule("beta", lambda ctx: ctx.get("user_role") == "beta_tester")
    assert provider.is_enabled("beta", {"user_role": "beta_tester"}) is True
    assert provider.is_enabled("beta", {"user_role": "regular"}) is False


def test_manager_require_raises():
    provider = InMemoryFeatureFlagProvider()
    mgr = FeatureFlagManager(provider)
    with pytest.raises(RuntimeError):
        mgr.require("disabled_feature")
