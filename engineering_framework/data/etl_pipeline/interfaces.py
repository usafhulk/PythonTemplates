"""ETL Pipeline Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Iterable


class Extractor(ABC):
    @abstractmethod
    def extract(self) -> Iterable[Any]: ...


class Transformer(ABC):
    @abstractmethod
    def transform(self, record: Any) -> Any: ...


class Loader(ABC):
    @abstractmethod
    def load(self, records: Iterable[Any]) -> int: ...


class Pipeline(ABC):
    @abstractmethod
    def run(self) -> dict: ...
