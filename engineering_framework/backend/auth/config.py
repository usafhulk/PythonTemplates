"""Auth Configuration."""
from dataclasses import dataclass


@dataclass
class AuthSettings:
    secret_key: str = "change-me-in-production"
    token_ttl_seconds: int = 3600
    algorithm: str = "HS256"
    refresh_enabled: bool = True
