"""Batch Processing Example."""
from engineering_framework.data.batch_processing.core import DefaultBatchJob, FunctionBatchProcessor

def normalize_record(record):
    return {"id": record["id"], "name": record["name"].strip().lower()}

processor = FunctionBatchProcessor(normalize_record)
job = DefaultBatchJob(processor, batch_size=100)

data = [{"id": i, "name": f"  User {i}  "} for i in range(500)]
result = job.run(data)
print(f"Processed: {result.total_records} records in {result.batches_processed} batches")
print(f"Duration: {result.duration_seconds}s")
