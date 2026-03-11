"""Task Scheduler Tests."""
import time
import pytest
from ..core import IntervalScheduler


def test_add_and_remove_job():
    scheduler = IntervalScheduler()
    job_id = scheduler.add_job(lambda: None, seconds=60)
    assert job_id in scheduler._jobs
    scheduler.remove_job(job_id)
    assert job_id not in scheduler._jobs


def test_job_executes():
    executed = []
    scheduler = IntervalScheduler()
    job_id = scheduler.add_job(lambda: executed.append(1), seconds=0.1)
    scheduler.start()
    time.sleep(0.5)
    scheduler.stop()
    assert len(executed) > 0
