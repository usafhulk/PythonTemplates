"""Rate Limiter Interfaces."""
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, tokens: int = 1) -> bool: ...

    @abstractmethod
    def reset(self) -> None: ...
