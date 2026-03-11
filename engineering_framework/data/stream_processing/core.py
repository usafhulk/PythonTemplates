"""Stream Processing Core."""
import logging
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from .interfaces import StreamProcessor, StreamRecord, StreamSink

logger = logging.getLogger(__name__)


class MapProcessor(StreamProcessor):
    def __init__(self, func: Callable[[StreamRecord], StreamRecord]) -> None:
        self._func = func

    def process(self, record: StreamRecord) -> Optional[StreamRecord]:
        return self._func(record)


class FilterProcessor(StreamProcessor):
    def __init__(self, predicate: Callable[[StreamRecord], bool]) -> None:
        self._predicate = predicate

    def process(self, record: StreamRecord) -> Optional[StreamRecord]:
        return record if self._predicate(record) else None


class WindowAggregator(StreamProcessor):
    """Tumbling window aggregator."""

    def __init__(self, window_size: int, agg_func: Callable[[List[Any]], Any]) -> None:
        self._window_size = window_size
        self._agg_func = agg_func
        self._buffer: List[StreamRecord] = []

    def process(self, record: StreamRecord) -> Optional[StreamRecord]:
        self._buffer.append(record)
        if len(self._buffer) >= self._window_size:
            values = [r.value for r in self._buffer]
            result = self._agg_func(values)
            self._buffer.clear()
            return StreamRecord(key="window_result", value=result, timestamp=time.time())
        return None


class InMemoryStreamSink(StreamSink):
    def __init__(self) -> None:
        self.records: List[StreamRecord] = []

    def write(self, record: StreamRecord) -> None:
        self.records.append(record)
        logger.debug("Stream record written: key=%s", record.key)


class StreamPipeline:
    def __init__(self, processors: Optional[List[StreamProcessor]] = None,
                 sink: Optional[StreamSink] = None) -> None:
        self._processors: List[StreamProcessor] = processors or []
        self._sink = sink or InMemoryStreamSink()

    def add_processor(self, processor: StreamProcessor) -> "StreamPipeline":
        self._processors.append(processor)
        return self

    def process_stream(self, records: List[StreamRecord]) -> int:
        written = 0
        for record in records:
            current: Optional[StreamRecord] = record
            for processor in self._processors:
                if current is None:
                    break
                current = processor.process(current)
            if current is not None:
                self._sink.write(current)
                written += 1
        return written
