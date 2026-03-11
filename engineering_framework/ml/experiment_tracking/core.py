"""Experiment Tracking Core."""
import logging
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from .interfaces import ExperimentTracker, Run

logger = logging.getLogger(__name__)


class InMemoryExperimentTracker(ExperimentTracker):
    """In-memory experiment tracker (replace with MLflow)."""

    def __init__(self) -> None:
        self._runs: Dict[str, Run] = {}

    def start_run(self, experiment_name: str) -> Run:
        run_id = str(uuid.uuid4())
        run = Run(run_id=run_id, experiment_name=experiment_name)
        self._runs[run_id] = run
        logger.info("Run started: %s (%s)", run_id, experiment_name)
        return run

    def log_param(self, run_id: str, key: str, value: Any) -> None:
        if run_id in self._runs:
            self._runs[run_id].params[key] = value

    def log_metric(self, run_id: str, key: str, value: float) -> None:
        if run_id in self._runs:
            self._runs[run_id].metrics[key] = value
            logger.debug("Metric logged: %s=%s (run=%s)", key, value, run_id)

    def end_run(self, run_id: str, status: str = "completed") -> None:
        if run_id in self._runs:
            self._runs[run_id].status = status
            logger.info("Run ended: %s (status=%s)", run_id, status)

    def get_run(self, run_id: str) -> Optional[Run]:
        return self._runs.get(run_id)

    def list_runs(self, experiment_name: str) -> List[Run]:
        return [r for r in self._runs.values() if r.experiment_name == experiment_name]

    @contextmanager
    def run(self, experiment_name: str) -> Generator[Run, None, None]:
        """Context manager for experiment runs."""
        active_run = self.start_run(experiment_name)
        try:
            yield active_run
            self.end_run(active_run.run_id, "completed")
        except Exception:
            self.end_run(active_run.run_id, "failed")
            raise
