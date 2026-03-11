"""Structured Logging Core."""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .interfaces import StructuredLogger


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "context"):
            log_data.update(record.context)  # type: ignore[attr-defined]
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class DefaultStructuredLogger(StructuredLogger):
    """Default structured logger using Python's logging module."""

    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._logger = logging.getLogger(name)
        self._context: Dict[str, Any] = context or {}
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        extra = {"context": {**self._context, **kwargs}}
        self._logger.log(level, message, extra=extra)

    def info(self, message: str, **context: Any) -> None:
        self._log(logging.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        self._log(logging.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._log(logging.ERROR, message, **context)

    def debug(self, message: str, **context: Any) -> None:
        self._log(logging.DEBUG, message, **context)

    def bind(self, **context: Any) -> "DefaultStructuredLogger":
        merged = {**self._context, **context}
        return DefaultStructuredLogger(self._logger.name, context=merged)


def get_logger(name: str) -> DefaultStructuredLogger:
    """Factory function to get a structured logger."""
    return DefaultStructuredLogger(name)
