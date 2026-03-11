"""REST API Core."""
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from .interfaces import APIRouter, Request, Response

logger = logging.getLogger(__name__)


class SimpleRouter(APIRouter):
    """Simple path-based router with parameter extraction."""

    def __init__(self) -> None:
        self._routes: List[Tuple[str, str, Callable]] = []

    def add_route(self, path: str, method: str, handler: Callable) -> None:
        self._routes.append((path, method.upper(), handler))
        logger.debug("Route registered: %s %s", method.upper(), path)

    def _match(self, pattern: str, path: str) -> Optional[Dict[str, str]]:
        regex = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', pattern)
        match = re.fullmatch(regex, path)
        return match.groupdict() if match else None

    def route(self, request: Request) -> Response:
        for route_path, route_method, handler in self._routes:
            if route_method != request.method.upper():
                continue
            params = self._match(route_path, request.path)
            if params is not None:
                request.path_params = params
                try:
                    return handler(request)
                except Exception as e:
                    logger.error("Handler error for %s %s: %s", request.method, request.path, e)
                    return Response(status_code=500, body={"error": str(e)})
        return Response(status_code=404, body={"error": "Not found"})


class APIService:
    """Minimal API service wrapper."""

    def __init__(self, router: Optional[APIRouter] = None) -> None:
        self._router = router or SimpleRouter()

    def get(self, path: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._router.add_route(path, "GET", func)
            return func
        return decorator

    def post(self, path: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self._router.add_route(path, "POST", func)
            return func
        return decorator

    def handle(self, request: Request) -> Response:
        return self._router.route(request)
