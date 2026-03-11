"""API Testing Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class APITestRequest:
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class APITestResponse:
    status_code: int
    body: Any
    headers: Dict[str, str] = field(default_factory=dict)
    duration_ms: float = 0.0


class APITestClient(ABC):
    @abstractmethod
    def send(self, request: APITestRequest) -> APITestResponse: ...
