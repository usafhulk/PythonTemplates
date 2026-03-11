"""Plugin Architecture Core."""
import importlib
import logging
from typing import Any, Dict, List, Optional, Type

from .interfaces import Plugin, PluginRegistry

logger = logging.getLogger(__name__)


class DefaultPluginRegistry(PluginRegistry):
    """Default in-memory plugin registry."""

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        if plugin.name in self._plugins:
            logger.warning("Plugin already registered: %s. Overwriting.", plugin.name)
        self._plugins[plugin.name] = plugin
        logger.info("Plugin registered: %s v%s", plugin.name, plugin.version)

    def get(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        return list(self._plugins.keys())

    def initialize_all(self, config: Dict[str, Any]) -> None:
        for plugin in self._plugins.values():
            try:
                plugin.initialize(config)
                logger.info("Plugin initialized: %s", plugin.name)
            except Exception as e:
                logger.error("Failed to initialize plugin %s: %s", plugin.name, e)

    def shutdown_all(self) -> None:
        for plugin in reversed(list(self._plugins.values())):
            try:
                plugin.shutdown()
                logger.info("Plugin shutdown: %s", plugin.name)
            except Exception as e:
                logger.error("Error shutting down plugin %s: %s", plugin.name, e)


class PluginBase(Plugin):
    """Convenient base class for plugins."""

    _name: str = "unnamed"
    _version: str = "0.1.0"

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def initialize(self, config: Dict[str, Any]) -> None:
        logger.debug("Plugin %s initialized with config keys: %s", self.name, list(config.keys()))

    def shutdown(self) -> None:
        logger.debug("Plugin %s shutdown", self.name)
