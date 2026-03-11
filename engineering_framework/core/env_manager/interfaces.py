"""Environment Manager Interfaces."""
from abc import ABC, abstractmethod
from enum import Enum


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class EnvironmentManager(ABC):
    @abstractmethod
    def current(self) -> Environment: ...

    @abstractmethod
    def is_production(self) -> bool: ...

    @abstractmethod
    def is_development(self) -> bool: ...
