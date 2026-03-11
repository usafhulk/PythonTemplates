"""REST API Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    query_params: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class Response:
    status_code: int
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)


class RouteHandler(ABC):
    @abstractmethod
    def handle(self, request: Request) -> Response: ...


class APIRouter(ABC):
    @abstractmethod
    def add_route(self, path: str, method: str, handler: Callable) -> None: ...

    @abstractmethod
    def route(self, request: Request) -> Response: ...
