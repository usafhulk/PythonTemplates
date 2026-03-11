"""Structured Logging Example."""
from engineering_framework.core.structured_logging.core import get_logger

logger = get_logger("myapp")
logger.info("Application started", version="1.0.0", env="production")

request_logger = logger.bind(request_id="req-abc123", user_id="user-42")
request_logger.info("Processing request", endpoint="/api/data")
request_logger.error("Request failed", status_code=500)
