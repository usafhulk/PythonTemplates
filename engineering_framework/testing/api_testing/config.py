"""API Testing Configuration."""
from dataclasses import dataclass


@dataclass
class APITestingSettings:
    base_url: str = "http://localhost:8000"
    timeout_seconds: float = 10.0
    verify_ssl: bool = True
    auth_token: str = ""
