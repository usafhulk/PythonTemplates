"""Middleware Interfaces."""
from abc import ABC, abstractmethod
from typing import Callable

from engineering_framework.backend.rest_api.interfaces import Request, Response


class Middleware(ABC):
    @abstractmethod
    def process(self, request: Request, next_handler: Callable[[Request], Response]) -> Response: ...
