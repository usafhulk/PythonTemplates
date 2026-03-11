"""Secrets Manager Interfaces."""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class SecretsManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]: ...

    @abstractmethod
    def set_secret(self, key: str, value: str) -> None: ...

    @abstractmethod
    def delete_secret(self, key: str) -> None: ...

    @abstractmethod
    def list_secrets(self) -> list: ...
