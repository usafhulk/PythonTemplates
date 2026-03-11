"""Feature Flags Example."""
from engineering_framework.core.feature_flags.core import InMemoryFeatureFlagProvider, FeatureFlagManager

provider = InMemoryFeatureFlagProvider()
provider.set_flag("new_dashboard", True)
provider.add_rule("beta_api", lambda ctx: ctx.get("plan") == "enterprise")

mgr = FeatureFlagManager(provider)
print(mgr.is_enabled("new_dashboard"))
print(mgr.is_enabled("beta_api", plan="enterprise"))
