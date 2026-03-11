"""Task Scheduler Example."""
import time
from engineering_framework.core.task_scheduler.core import IntervalScheduler

scheduler = IntervalScheduler()

def cleanup_task():
    print("Running cleanup...")

job_id = scheduler.add_job(cleanup_task, seconds=5)
scheduler.start()
time.sleep(0.1)
scheduler.stop()
print(f"Scheduled job: {job_id}")
