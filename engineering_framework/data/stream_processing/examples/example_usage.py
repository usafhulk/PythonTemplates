"""Stream Processing Example."""
import time
from engineering_framework.data.stream_processing.core import (
    StreamPipeline, MapProcessor, FilterProcessor, InMemoryStreamSink
)
from engineering_framework.data.stream_processing.interfaces import StreamRecord

sink = InMemoryStreamSink()
pipeline = StreamPipeline(sink=sink)
pipeline.add_processor(FilterProcessor(lambda r: r.value.get("active", False)))
pipeline.add_processor(MapProcessor(lambda r: StreamRecord(
    key=r.key, value={**r.value, "processed": True}, timestamp=time.time()
)))

events = [
    StreamRecord(key="e1", value={"user": "alice", "active": True}),
    StreamRecord(key="e2", value={"user": "bob", "active": False}),
    StreamRecord(key="e3", value={"user": "charlie", "active": True}),
]
written = pipeline.process_stream(events)
print(f"Written: {written}")
print(sink.records)
