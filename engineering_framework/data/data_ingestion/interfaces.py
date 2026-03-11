"""Data Ingestion Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass
class IngestionResult:
    records_ingested: int
    source: str
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def read(self) -> Iterable[Dict[str, Any]]: ...


class IngestionService(ABC):
    @abstractmethod
    def ingest(self, source: DataSource) -> IngestionResult: ...
