"""Distributed Lock Example."""
from engineering_framework.distributed.distributed_lock.core import InMemoryDistributedLock

lock = InMemoryDistributedLock()
with lock.lock("batch_job", ttl_seconds=300) as acquired:
    print(f"Lock acquired: {acquired}")
