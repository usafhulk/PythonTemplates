"""Secrets Manager Core."""
import logging
import os
from typing import Dict, List, Optional

from .interfaces import SecretsManager

logger = logging.getLogger(__name__)


class InMemorySecretsManager(SecretsManager):
    """In-memory secrets manager for testing (use AWS SSM/Vault in production)."""

    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}

    def get_secret(self, key: str) -> Optional[str]:
        value = self._secrets.get(key)
        if value is None:
            logger.warning("Secret not found: %s", key)
        else:
            logger.debug("Secret retrieved: %s", key)
        return value

    def set_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value
        logger.info("Secret set: %s", key)

    def delete_secret(self, key: str) -> None:
        if key in self._secrets:
            del self._secrets[key]
            logger.info("Secret deleted: %s", key)

    def list_secrets(self) -> List[str]:
        return list(self._secrets.keys())


class EnvSecretsManager(SecretsManager):
    """Reads secrets from environment variables."""

    def __init__(self, prefix: str = "") -> None:
        self._prefix = prefix.upper()

    def _key(self, key: str) -> str:
        return f"{self._prefix}_{key.upper()}" if self._prefix else key.upper()

    def get_secret(self, key: str) -> Optional[str]:
        value = os.environ.get(self._key(key))
        if value is None:
            logger.warning("Env secret not found: %s", self._key(key))
        return value

    def set_secret(self, key: str, value: str) -> None:
        os.environ[self._key(key)] = value

    def delete_secret(self, key: str) -> None:
        os.environ.pop(self._key(key), None)

    def list_secrets(self) -> List[str]:
        prefix = self._prefix + "_" if self._prefix else ""
        return [k for k in os.environ if k.startswith(prefix)]
