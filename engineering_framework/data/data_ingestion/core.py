"""Data Ingestion Core."""
import csv
import io
import json
import logging
from typing import Any, Dict, Iterable, List

from .interfaces import DataSource, IngestionResult, IngestionService

logger = logging.getLogger(__name__)


class JSONDataSource(DataSource):
    def __init__(self, data: List[Dict[str, Any]], source_name: str = "json") -> None:
        self._data = data
        self._name = source_name

    @property
    def name(self) -> str:
        return self._name

    def read(self) -> Iterable[Dict[str, Any]]:
        return iter(self._data)


class CSVDataSource(DataSource):
    def __init__(self, csv_content: str, source_name: str = "csv") -> None:
        self._csv = csv_content
        self._name = source_name

    @property
    def name(self) -> str:
        return self._name

    def read(self) -> Iterable[Dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(self._csv))
        return list(reader)


class DefaultIngestionService(IngestionService):
    def __init__(self) -> None:
        self._sink: List[Dict[str, Any]] = []

    def ingest(self, source: DataSource) -> IngestionResult:
        errors = []
        count = 0
        for record in source.read():
            try:
                self._sink.append(record)
                count += 1
            except Exception as e:
                errors.append(str(e))
        logger.info("Ingested %d records from %s", count, source.name)
        return IngestionResult(records_ingested=count, source=source.name, errors=errors)

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._sink
