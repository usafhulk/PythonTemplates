"""Task Scheduler Core."""
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .interfaces import Scheduler

logger = logging.getLogger(__name__)


@dataclass
class Job:
    job_id: str
    func: Callable[..., Any]
    interval_seconds: float
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    last_run: float = 0.0
    enabled: bool = True


class IntervalScheduler(Scheduler):
    """Simple interval-based task scheduler."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_job(self, func: Callable[..., Any], trigger: str = "interval",
                seconds: float = 60.0, **kwargs: Any) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = Job(job_id=job_id, func=func, interval_seconds=seconds)
        logger.info("Job added: %s (every %ss)", job_id, seconds)
        return job_id

    def remove_job(self, job_id: str) -> None:
        self._jobs.pop(job_id, None)
        logger.info("Job removed: %s", job_id)

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        self._running = False
        logger.info("Scheduler stopped")

    def _run_loop(self) -> None:
        while self._running:
            now = time.time()
            for job in list(self._jobs.values()):
                if job.enabled and now - job.last_run >= job.interval_seconds:
                    job.last_run = now
                    try:
                        job.func(*job.args, **job.kwargs)
                    except Exception as e:
                        logger.error("Job %s failed: %s", job.job_id, e)
            time.sleep(1.0)
