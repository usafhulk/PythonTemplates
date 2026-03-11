"""Data Ingestion Tests."""
import pytest
from ..core import JSONDataSource, CSVDataSource, DefaultIngestionService


def test_json_ingestion():
    data = [{"id": 1}, {"id": 2}]
    source = JSONDataSource(data)
    service = DefaultIngestionService()
    result = service.ingest(source)
    assert result.records_ingested == 2
    assert result.source == "json"


def test_csv_ingestion():
    csv_content = "id,name\n1,Alice\n2,Bob\n"
    source = CSVDataSource(csv_content)
    service = DefaultIngestionService()
    result = service.ingest(source)
    assert result.records_ingested == 2


def test_ingestion_stores_data():
    data = [{"x": i} for i in range(5)]
    source = JSONDataSource(data)
    service = DefaultIngestionService()
    service.ingest(source)
    assert len(service.data) == 5
