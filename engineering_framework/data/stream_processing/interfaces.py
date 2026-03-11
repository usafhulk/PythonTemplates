"""Stream Processing Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional


@dataclass
class StreamRecord:
    key: str
    value: Any
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamProcessor(ABC):
    @abstractmethod
    def process(self, record: StreamRecord) -> Optional[StreamRecord]: ...


class StreamSink(ABC):
    @abstractmethod
    def write(self, record: StreamRecord) -> None: ...
