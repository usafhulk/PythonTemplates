"""Auth Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AuthToken:
    token: str
    subject: str
    claims: Dict[str, Any]


@dataclass
class Credentials:
    username: str
    password: str


class Authenticator(ABC):
    @abstractmethod
    def authenticate(self, credentials: Credentials) -> Optional[AuthToken]: ...

    @abstractmethod
    def verify_token(self, token: str) -> Optional[AuthToken]: ...
