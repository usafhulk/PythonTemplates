"""Error Handling Tests."""
import pytest
from ..core import (AppError, ValidationError, NotFoundError, UnauthorizedError,
                   DefaultErrorClassifier, LoggingErrorHandler, ErrorHandlerChain)


def test_app_error_attributes():
    err = AppError("test error", code="TEST_CODE", details={"key": "val"})
    assert err.code == "TEST_CODE"
    assert err.details["key"] == "val"


def test_validation_error():
    err = ValidationError("Invalid email", field="email")
    assert err.code == "VALIDATION_ERROR"
    assert err.details["field"] == "email"


def test_not_found_error():
    err = NotFoundError("User", identifier=42)
    assert err.code == "NOT_FOUND"
    assert "not found" in str(err)


def test_classifier():
    clf = DefaultErrorClassifier()
    assert clf.classify(ValidationError("bad")) == "validation"
    assert clf.classify(NotFoundError("item")) == "not_found"
    assert clf.classify(RuntimeError("boom")) == "system"


def test_error_handler_chain():
    chain = ErrorHandlerChain()
    handler = LoggingErrorHandler()
    chain.add_handler(handler)
    chain.handle(ValidationError("bad input"), context={"endpoint": "/api"})
