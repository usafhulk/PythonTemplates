"""Environment Manager Configuration."""
from dataclasses import dataclass


@dataclass
class EnvironmentSettings:
    env_var: str = "APP_ENV"
    default_env: str = "development"
