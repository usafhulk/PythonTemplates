"""Environment Manager Core."""
import logging
import os
from typing import Optional

from .interfaces import Environment, EnvironmentManager

logger = logging.getLogger(__name__)

_ENV_MAP = {
    "development": Environment.DEVELOPMENT,
    "dev": Environment.DEVELOPMENT,
    "staging": Environment.STAGING,
    "stage": Environment.STAGING,
    "production": Environment.PRODUCTION,
    "prod": Environment.PRODUCTION,
    "test": Environment.TEST,
}


class DefaultEnvironmentManager(EnvironmentManager):
    """Reads environment from APP_ENV or ENVIRONMENT variable."""

    def __init__(self, env_var: str = "APP_ENV", default: Environment = Environment.DEVELOPMENT) -> None:
        self._env_var = env_var
        self._default = default
        self._override: Optional[Environment] = None

    def current(self) -> Environment:
        if self._override is not None:
            return self._override
        raw = os.environ.get(self._env_var, "").lower()
        env = _ENV_MAP.get(raw, self._default)
        logger.debug("Current environment: %s", env.value)
        return env

    def set(self, env: Environment) -> None:
        self._override = env

    def is_production(self) -> bool:
        return self.current() == Environment.PRODUCTION

    def is_development(self) -> bool:
        return self.current() == Environment.DEVELOPMENT

    def is_test(self) -> bool:
        return self.current() == Environment.TEST
