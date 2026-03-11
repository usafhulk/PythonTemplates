"""Plugin Architecture Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None: ...

    @abstractmethod
    def shutdown(self) -> None: ...


class PluginRegistry(ABC):
    @abstractmethod
    def register(self, plugin: Plugin) -> None: ...

    @abstractmethod
    def get(self, name: str) -> Optional[Plugin]: ...

    @abstractmethod
    def list_plugins(self) -> list: ...
