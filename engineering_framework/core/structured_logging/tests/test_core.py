"""Structured Logging Tests."""
import json
import logging
import pytest
from io import StringIO
from ..core import DefaultStructuredLogger, get_logger, JSONFormatter


def test_json_formatter_output():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hello", args=(), exc_info=None
    )
    output = formatter.format(record)
    data = json.loads(output)
    assert data["message"] == "hello"
    assert data["level"] == "INFO"


def test_logger_bind_context():
    logger = get_logger("test")
    bound = logger.bind(request_id="abc123")
    assert bound._context.get("request_id") == "abc123"


def test_logger_factory():
    logger = get_logger("myapp")
    assert logger is not None
    logger.info("test message", user_id=42)
