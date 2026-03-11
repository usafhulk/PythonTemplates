"""Job Queue Core."""
import logging
import queue
import threading
import time
import uuid
from typing import Any, Callable, Dict, Optional

from .interfaces import Job, JobHandler, JobQueue, JobStatus

logger = logging.getLogger(__name__)


class InMemoryJobQueue(JobQueue):
    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue()
        self._jobs: Dict[str, Job] = {}

    def enqueue(self, job_type: str, payload: Dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, job_type=job_type, payload=payload)
        self._jobs[job_id] = job
        self._queue.put(job)
        logger.info("Job enqueued: %s (type=%s)", job_id, job_type)
        return job_id

    def dequeue(self) -> Optional[Job]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)


class JobWorker:
    def __init__(self, job_queue: JobQueue, handlers: Dict[str, JobHandler]) -> None:
        self._queue = job_queue
        self._handlers = handlers
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Job worker started")

    def stop(self) -> None:
        self._running = False

    def _process_loop(self) -> None:
        while self._running:
            job = self._queue.dequeue()
            if job:
                self._process(job)
            else:
                time.sleep(0.1)

    def _process(self, job: Job) -> None:
        handler = self._handlers.get(job.job_type)
        if not handler:
            logger.error("No handler for job type: %s", job.job_type)
            job.status = JobStatus.FAILED
            job.error = f"No handler for {job.job_type}"
            return
        job.status = JobStatus.RUNNING
        try:
            job.result = handler.handle(job)
            job.status = JobStatus.COMPLETED
            logger.info("Job completed: %s", job.job_id)
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error("Job failed: %s - %s", job.job_id, e)
