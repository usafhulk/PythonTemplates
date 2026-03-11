"""Error Handling Core."""
import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Type

from .interfaces import ErrorClassifier, ErrorHandler

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "UNKNOWN", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ValidationError(AppError):
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", details={"field": field})


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: Any = None) -> None:
        super().__init__(f"{resource} not found", code="NOT_FOUND", details={"resource": resource, "id": identifier})


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="UNAUTHORIZED")


class DefaultErrorClassifier(ErrorClassifier):
    def classify(self, error: Exception) -> str:
        if isinstance(error, ValidationError):
            return "validation"
        if isinstance(error, NotFoundError):
            return "not_found"
        if isinstance(error, UnauthorizedError):
            return "unauthorized"
        if isinstance(error, AppError):
            return "application"
        return "system"


class LoggingErrorHandler(ErrorHandler):
    def __init__(self, classifier: Optional[ErrorClassifier] = None) -> None:
        self._classifier = classifier or DefaultErrorClassifier()

    def handle(self, error: Exception, context: Optional[Any] = None) -> None:
        category = self._classifier.classify(error)
        logger.error(
            "Error handled",
            extra={"context": {
                "error_type": type(error).__name__,
                "error_category": category,
                "message": str(error),
                "context": str(context),
                "traceback": traceback.format_exc(),
            }}
        )


class ErrorHandlerChain:
    """Chain of error handlers."""

    def __init__(self) -> None:
        self._handlers: List[ErrorHandler] = []

    def add_handler(self, handler: ErrorHandler) -> "ErrorHandlerChain":
        self._handlers.append(handler)
        return self

    def handle(self, error: Exception, context: Optional[Any] = None) -> None:
        for handler in self._handlers:
            handler.handle(error, context)
