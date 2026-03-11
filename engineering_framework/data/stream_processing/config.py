"""Stream Processing Configuration."""
from dataclasses import dataclass


@dataclass
class StreamSettings:
    backend: str = "inmemory"
    kafka_brokers: str = "localhost:9092"
    consumer_group: str = "default"
    batch_size: int = 100
    window_size: int = 1000
