"""Config Service Configuration."""
from dataclasses import dataclass


@dataclass
class ConfigServiceSettings:
    backend: str = "inmemory"
    etcd_url: str = "http://localhost:2379"
    polling_interval: int = 30
