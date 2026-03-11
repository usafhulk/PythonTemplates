"""Job Queue Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    job_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


class JobQueue(ABC):
    @abstractmethod
    def enqueue(self, job_type: str, payload: Dict[str, Any]) -> str: ...

    @abstractmethod
    def dequeue(self) -> Optional[Job]: ...

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]: ...


class JobHandler(ABC):
    @abstractmethod
    def handle(self, job: Job) -> Any: ...
