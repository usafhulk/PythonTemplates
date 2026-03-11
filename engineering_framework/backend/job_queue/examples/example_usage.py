"""Job Queue Example."""
import time
from engineering_framework.backend.job_queue.core import InMemoryJobQueue, JobWorker
from engineering_framework.backend.job_queue.interfaces import Job, JobHandler

class SendEmailHandler(JobHandler):
    def handle(self, job: Job):
        print(f"Sending email to: {job.payload.get('to')}")
        return {"sent": True}

q = InMemoryJobQueue()
worker = JobWorker(q, {"send_email": SendEmailHandler()})
worker.start()
q.enqueue("send_email", {"to": "alice@example.com", "subject": "Hello"})
time.sleep(0.5)
worker.stop()
