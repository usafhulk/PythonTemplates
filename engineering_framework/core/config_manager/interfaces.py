"""Config Manager Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ConfigSource(ABC):
    """Abstract base for configuration sources."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a config value by key."""
        ...

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load all config values."""
        ...


class ConfigManager(ABC):
    """Abstract configuration manager."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        ...

    @abstractmethod
    def reload(self) -> None:
        """Reload all configuration sources."""
        ...
