"""Feature Store Tests."""
import pytest
from ..core import InMemoryFeatureStore
from ..interfaces import FeatureGroup


def test_write_and_read_features():
    store = InMemoryFeatureStore()
    store.write_features("user:1", "user_features", {"age": 30, "score": 0.85})
    features = store.get_features("user:1", ["user_features.age", "user_features.score"])
    assert features["user_features.age"] == 30
    assert features["user_features.score"] == 0.85


def test_register_feature_group():
    store = InMemoryFeatureStore()
    group = FeatureGroup(name="user_features", features=["age", "score"])
    store.register_feature_group(group)
    assert "user_features" in store._groups


def test_get_feature_vector():
    store = InMemoryFeatureStore()
    store.write_features("user:2", "order_features", {"order_count": 5, "avg_value": 42.5})
    vector = store.get_feature_vector("user:2", "order_features")
    assert vector["order_count"] == 5
    assert vector["avg_value"] == 42.5


def test_missing_entity():
    store = InMemoryFeatureStore()
    features = store.get_features("unknown:999", ["some.feature"])
    assert features["some.feature"] is None
