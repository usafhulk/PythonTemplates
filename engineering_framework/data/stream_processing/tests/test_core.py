"""Stream Processing Tests."""
from typing import Any
import pytest
from ..core import (MapProcessor, FilterProcessor, WindowAggregator,
                   InMemoryStreamSink, StreamPipeline)
from ..interfaces import StreamRecord


def make_record(key: str, value: Any) -> StreamRecord:
    import time
    return StreamRecord(key=key, value=value, timestamp=time.time())


def test_map_processor():
    proc = MapProcessor(lambda r: StreamRecord(key=r.key, value=r.value * 2, timestamp=r.timestamp))
    result = proc.process(make_record("x", 5))
    assert result.value == 10


def test_filter_processor():
    proc = FilterProcessor(lambda r: r.value > 3)
    assert proc.process(make_record("x", 5)) is not None
    assert proc.process(make_record("y", 1)) is None


def test_window_aggregator():
    agg = WindowAggregator(window_size=3, agg_func=sum)
    r = None
    for i in range(1, 4):
        r = agg.process(make_record("x", i))
    assert r is not None
    assert r.value == 6  # 1+2+3


def test_pipeline():
    sink = InMemoryStreamSink()
    pipeline = StreamPipeline(sink=sink)
    pipeline.add_processor(FilterProcessor(lambda r: r.value > 0))
    records = [make_record("k", v) for v in [-1, 1, 2, -3, 4]]
    written = pipeline.process_stream(records)
    assert written == 3
    assert len(sink.records) == 3
