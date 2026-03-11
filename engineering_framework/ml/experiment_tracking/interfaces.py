"""Experiment Tracking Interfaces."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Run:
    run_id: str
    experiment_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    status: str = "running"
    artifacts: List[str] = field(default_factory=list)


class ExperimentTracker(ABC):
    @abstractmethod
    def start_run(self, experiment_name: str) -> Run: ...

    @abstractmethod
    def log_param(self, run_id: str, key: str, value: Any) -> None: ...

    @abstractmethod
    def log_metric(self, run_id: str, key: str, value: float) -> None: ...

    @abstractmethod
    def end_run(self, run_id: str, status: str = "completed") -> None: ...

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[Run]: ...
