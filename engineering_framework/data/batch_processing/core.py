"""Batch Processing Core."""
import logging
import time
from typing import Any, Callable, Iterable, Iterator, List, Optional

from .interfaces import BatchJob, BatchProcessor, BatchResult

logger = logging.getLogger(__name__)


def chunk_iterator(iterable: Iterable[Any], size: int) -> Iterator[List[Any]]:
    """Split iterable into chunks of given size."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


class FunctionBatchProcessor(BatchProcessor):
    def __init__(self, func: Callable[[Any], Any]) -> None:
        self._func = func

    def process_batch(self, batch: List[Any]) -> List[Any]:
        results = []
        for item in batch:
            results.append(self._func(item))
        return results


class DefaultBatchJob(BatchJob):
    def __init__(self, processor: BatchProcessor, batch_size: int = 1000) -> None:
        self._processor = processor
        self._batch_size = batch_size

    def run(self, data: Iterable[Any]) -> BatchResult:
        start = time.time()
        total = 0
        failed = 0
        batches = 0
        for batch in chunk_iterator(data, self._batch_size):
            try:
                self._processor.process_batch(batch)
                total += len(batch)
                batches += 1
                logger.debug("Batch %d processed (%d records)", batches, len(batch))
            except Exception as e:
                logger.error("Batch %d failed: %s", batches + 1, e)
                failed += len(batch)
                batches += 1
        elapsed = time.time() - start
        result = BatchResult(
            batches_processed=batches,
            total_records=total,
            failed_records=failed,
            duration_seconds=round(elapsed, 3),
        )
        logger.info("Batch job completed: %s", result)
        return result
