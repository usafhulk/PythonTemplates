"""Config Manager Core Implementation."""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .interfaces import ConfigManager, ConfigSource

logger = logging.getLogger(__name__)


class EnvConfigSource(ConfigSource):
    """Configuration source from environment variables."""

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.upper()

    def get(self, key: str, default: Any = None) -> Any:
        env_key = f"{self.prefix}_{key.upper()}" if self.prefix else key.upper()
        return os.environ.get(env_key, default)

    def load(self) -> Dict[str, Any]:
        if self.prefix:
            return {
                k[len(self.prefix) + 1:].lower(): v
                for k, v in os.environ.items()
                if k.startswith(self.prefix + "_")
            }
        return dict(os.environ)


class FileConfigSource(ConfigSource):
    """Configuration source from JSON/dict files."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        if not self._data:
            self.load()
        return self._data.get(key, default)

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)
            logger.info("Loaded config from %s", self.path)
        else:
            logger.warning("Config file not found: %s", self.path)
            self._data = {}
        return self._data


class DefaultConfigManager(ConfigManager):
    """Default config manager with layered sources (later sources override earlier)."""

    def __init__(self, sources: Optional[List[ConfigSource]] = None) -> None:
        self._sources: List[ConfigSource] = sources or []
        self._overrides: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}

    def add_source(self, source: ConfigSource) -> None:
        """Add a config source."""
        self._sources.append(source)
        self._cache.clear()

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._overrides:
            return self._overrides[key]
        if key in self._cache:
            return self._cache[key]
        for source in reversed(self._sources):
            value = source.get(key)
            if value is not None:
                self._cache[key] = value
                return value
        return default

    def set(self, key: str, value: Any) -> None:
        self._overrides[key] = value
        self._cache[key] = value
        logger.debug("Config override set: %s", key)

    def reload(self) -> None:
        self._cache.clear()
        for source in self._sources:
            source.load()
        logger.info("Config reloaded from %d sources", len(self._sources))
