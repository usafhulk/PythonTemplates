"""Batch Processing Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass
class BatchResult:
    batches_processed: int
    total_records: int
    failed_records: int
    duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class BatchProcessor(ABC):
    @abstractmethod
    def process_batch(self, batch: List[Any]) -> List[Any]: ...


class BatchJob(ABC):
    @abstractmethod
    def run(self, data: Iterable[Any]) -> BatchResult: ...
