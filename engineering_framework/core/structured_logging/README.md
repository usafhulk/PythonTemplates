# Structured Logging

JSON-formatted structured logging with context propagation and binding.

## Features
- JSON output format
- Context binding (request ID, user ID, etc.)
- Extensible formatter
- Python logging integration

## Usage
```python
from engineering_framework.core.structured_logging.core import get_logger
logger = get_logger("myapp")
logger.info("Started", version="1.0")
bound = logger.bind(request_id="abc")
bound.error("Failed", code=500)
```
