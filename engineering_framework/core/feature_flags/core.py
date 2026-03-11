"""Feature Flags Core."""
import logging
from typing import Any, Callable, Dict, Optional

from .interfaces import FeatureFlagProvider

logger = logging.getLogger(__name__)


class InMemoryFeatureFlagProvider(FeatureFlagProvider):
    """Simple in-memory feature flag provider."""

    def __init__(self) -> None:
        self._flags: Dict[str, Any] = {}
        self._rules: Dict[str, Callable[[Dict[str, Any]], bool]] = {}

    def set_flag(self, flag: str, enabled: bool) -> None:
        self._flags[flag] = enabled
        logger.info("Feature flag set: %s=%s", flag, enabled)

    def add_rule(self, flag: str, rule: Callable[[Dict[str, Any]], bool]) -> None:
        self._rules[flag] = rule

    def is_enabled(self, flag: str, context: Dict[str, Any] = {}) -> bool:
        if flag in self._rules:
            result = self._rules[flag](context)
            logger.debug("Flag %s evaluated by rule: %s", flag, result)
            return result
        return bool(self._flags.get(flag, False))

    def get_variant(self, flag: str, context: Dict[str, Any] = {}) -> str:
        return "enabled" if self.is_enabled(flag, context) else "disabled"


class FeatureFlagManager:
    """Convenience wrapper around a provider."""

    def __init__(self, provider: FeatureFlagProvider) -> None:
        self._provider = provider

    def is_enabled(self, flag: str, **context: Any) -> bool:
        return self._provider.is_enabled(flag, context)

    def require(self, flag: str, **context: Any) -> None:
        if not self.is_enabled(flag, **context):
            raise RuntimeError(f"Feature '{flag}' is not enabled")
