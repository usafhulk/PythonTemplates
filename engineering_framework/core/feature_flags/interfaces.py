"""Feature Flags Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class FeatureFlagProvider(ABC):
    @abstractmethod
    def is_enabled(self, flag: str, context: Dict[str, Any] = {}) -> bool: ...

    @abstractmethod
    def get_variant(self, flag: str, context: Dict[str, Any] = {}) -> str: ...
