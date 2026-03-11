"""Error Handling Example."""
from engineering_framework.core.error_handling.core import (
    ValidationError, NotFoundError, LoggingErrorHandler, ErrorHandlerChain
)

chain = ErrorHandlerChain()
chain.add_handler(LoggingErrorHandler())

try:
    raise ValidationError("Invalid email address", field="email")
except Exception as e:
    chain.handle(e, context={"user_id": "u123"})
