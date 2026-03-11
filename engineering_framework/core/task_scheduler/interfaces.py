"""Task Scheduler Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Callable


class Scheduler(ABC):
    @abstractmethod
    def add_job(self, func: Callable[..., Any], trigger: str, **kwargs: Any) -> str: ...

    @abstractmethod
    def remove_job(self, job_id: str) -> None: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
