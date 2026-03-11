"""Data Ingestion Example."""
from engineering_framework.data.data_ingestion.core import (
    JSONDataSource, CSVDataSource, DefaultIngestionService
)

service = DefaultIngestionService()
json_source = JSONDataSource([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
result = service.ingest(json_source)
print(f"Ingested {result.records_ingested} records from {result.source}")

csv_source = CSVDataSource("id,value\n1,100\n2,200\n3,300")
result2 = service.ingest(csv_source)
print(f"Ingested {result2.records_ingested} CSV records")
print(f"Total stored: {len(service.data)}")
