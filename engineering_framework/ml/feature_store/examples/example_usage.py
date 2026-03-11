"""Feature Store Example."""
from engineering_framework.ml.feature_store.core import InMemoryFeatureStore
from engineering_framework.ml.feature_store.interfaces import FeatureGroup

store = InMemoryFeatureStore()
store.register_feature_group(FeatureGroup(
    name="user_behavior",
    features=["session_count", "avg_session_duration", "purchase_rate"]
))

store.write_features("user:42", "user_behavior", {
    "session_count": 15,
    "avg_session_duration": 120.5,
    "purchase_rate": 0.23,
})

vector = store.get_feature_vector("user:42", "user_behavior")
print(f"Feature vector for user:42: {vector}")
