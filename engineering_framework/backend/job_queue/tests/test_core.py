"""Job Queue Tests."""
import time
import pytest
from ..core import InMemoryJobQueue, JobWorker
from ..interfaces import Job, JobHandler, JobStatus


class EchoHandler(JobHandler):
    def handle(self, job: Job):
        return {"echo": job.payload}


def test_enqueue_and_dequeue():
    q = InMemoryJobQueue()
    job_id = q.enqueue("echo", {"message": "hello"})
    job = q.dequeue()
    assert job is not None
    assert job.job_id == job_id


def test_get_job():
    q = InMemoryJobQueue()
    job_id = q.enqueue("echo", {"x": 1})
    job = q.get_job(job_id)
    assert job is not None
    assert job.status == JobStatus.PENDING


def test_worker_processes_job():
    q = InMemoryJobQueue()
    handlers = {"echo": EchoHandler()}
    worker = JobWorker(q, handlers)
    job_id = q.enqueue("echo", {"msg": "test"})
    worker.start()
    time.sleep(0.5)
    worker.stop()
    job = q.get_job(job_id)
    assert job.status == JobStatus.COMPLETED
    assert job.result == {"echo": {"msg": "test"}}
