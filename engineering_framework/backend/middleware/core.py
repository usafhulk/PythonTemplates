"""Middleware Core."""
import logging
import time
import uuid
from typing import Callable, List

from engineering_framework.backend.rest_api.interfaces import Request, Response
from .interfaces import Middleware

logger = logging.getLogger(__name__)


class MiddlewarePipeline:
    """Chains multiple middleware components."""

    def __init__(self) -> None:
        self._middlewares: List[Middleware] = []

    def add(self, middleware: Middleware) -> "MiddlewarePipeline":
        self._middlewares.append(middleware)
        return self

    def execute(self, request: Request, final_handler: Callable[[Request], Response]) -> Response:
        def build_chain(index: int) -> Callable[[Request], Response]:
            if index >= len(self._middlewares):
                return final_handler
            mw = self._middlewares[index]
            return lambda req: mw.process(req, build_chain(index + 1))
        return build_chain(0)(request)


class LoggingMiddleware(Middleware):
    def process(self, request: Request, next_handler: Callable[[Request], Response]) -> Response:
        start = time.perf_counter()
        logger.info("Request: %s %s", request.method, request.path)
        response = next_handler(request)
        elapsed = time.perf_counter() - start
        logger.info("Response: %d in %.3fs", response.status_code, elapsed)
        return response


class RequestIDMiddleware(Middleware):
    def process(self, request: Request, next_handler: Callable[[Request], Response]) -> Response:
        request.headers["X-Request-ID"] = str(uuid.uuid4())
        return next_handler(request)


class CORSMiddleware(Middleware):
    def __init__(self, allowed_origins: str = "*") -> None:
        self.allowed_origins = allowed_origins

    def process(self, request: Request, next_handler: Callable[[Request], Response]) -> Response:
        response = next_handler(request)
        response.headers["Access-Control-Allow-Origin"] = self.allowed_origins
        return response
