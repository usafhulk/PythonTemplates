"""REST API Configuration."""
from dataclasses import dataclass


@dataclass
class APISettings:
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_enabled: bool = True
    allowed_origins: str = "*"
    request_timeout: int = 30
