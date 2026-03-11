"""Distributed Lock Tests."""
import time
import pytest
from ..core import InMemoryDistributedLock


def test_acquire_and_release():
    lock = InMemoryDistributedLock()
    assert lock.acquire("r1") is True
    assert lock.is_locked("r1") is True
    lock.release("r1")
    assert lock.is_locked("r1") is False


def test_cannot_acquire_held_lock():
    lock = InMemoryDistributedLock()
    lock.acquire("r2", ttl_seconds=60)
    assert lock.acquire("r2") is False


def test_ttl_expiry():
    lock = InMemoryDistributedLock()
    lock.acquire("r3", ttl_seconds=0)
    time.sleep(0.01)
    assert lock.is_locked("r3") is False


def test_context_manager():
    lock = InMemoryDistributedLock()
    with lock.lock("r4") as acquired:
        assert acquired is True
    assert lock.is_locked("r4") is False
