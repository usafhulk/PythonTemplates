"""Secrets Manager Configuration."""
from dataclasses import dataclass


@dataclass
class SecretsManagerSettings:
    backend: str = "inmemory"
    vault_url: str = "http://localhost:8200"
    aws_region: str = "us-east-1"
    cache_ttl_seconds: int = 300
    encryption_enabled: bool = True
