"""Batch Processing Tests."""
import pytest
from ..core import DefaultBatchJob, FunctionBatchProcessor, chunk_iterator


def test_chunk_iterator():
    data = list(range(10))
    chunks = list(chunk_iterator(data, 3))
    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[-1] == [9]


def test_batch_job_runs():
    processor = FunctionBatchProcessor(lambda x: x * 2)
    job = DefaultBatchJob(processor, batch_size=5)
    result = job.run(range(20))
    assert result.total_records == 20
    assert result.batches_processed == 4
    assert result.failed_records == 0


def test_batch_job_small_dataset():
    processor = FunctionBatchProcessor(str)
    job = DefaultBatchJob(processor, batch_size=100)
    result = job.run(range(5))
    assert result.total_records == 5
    assert result.batches_processed == 1
