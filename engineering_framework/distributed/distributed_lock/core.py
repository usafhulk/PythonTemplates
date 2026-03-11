"""Distributed Lock Core."""
import logging
import threading
import time
from contextlib import contextmanager
from typing import Dict, Generator, Tuple

from .interfaces import DistributedLock

logger = logging.getLogger(__name__)


class InMemoryDistributedLock(DistributedLock):
    def __init__(self) -> None:
        self._locks: Dict[str, Tuple[float, float]] = {}
        self._mutex = threading.Lock()

    def acquire(self, name: str, ttl_seconds: int = 30) -> bool:
        with self._mutex:
            now = time.time()
            if name in self._locks:
                _, expires_at = self._locks[name]
                if now < expires_at:
                    return False
            self._locks[name] = (now, now + ttl_seconds)
            logger.info("Lock acquired: %s", name)
            return True

    def release(self, name: str) -> None:
        with self._mutex:
            self._locks.pop(name, None)

    def is_locked(self, name: str) -> bool:
        with self._mutex:
            if name not in self._locks:
                return False
            _, expires_at = self._locks[name]
            if time.time() >= expires_at:
                del self._locks[name]
                return False
            return True

    @contextmanager
    def lock(self, name: str, ttl_seconds: int = 30, retry_attempts: int = 3,
             retry_delay: float = 0.1) -> Generator[bool, None, None]:
        acquired = False
        for _ in range(retry_attempts):
            if self.acquire(name, ttl_seconds):
                acquired = True
                break
            time.sleep(retry_delay)
        try:
            yield acquired
        finally:
            if acquired:
                self.release(name)
