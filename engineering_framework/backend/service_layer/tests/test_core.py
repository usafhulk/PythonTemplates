"""Service Layer Tests."""
import pytest
from dataclasses import dataclass, field
from typing import Optional
from ..core import InMemoryRepository, ServiceResult


@dataclass
class User:
    id: Optional[str]
    name: str
    email: str


def test_save_and_find():
    repo = InMemoryRepository()
    user = User(id="u1", name="Alice", email="alice@example.com")
    repo.save(user)
    found = repo.find_by_id("u1")
    assert found is not None
    assert found.name == "Alice"


def test_find_all():
    repo = InMemoryRepository()
    repo.save(User(id="u1", name="Alice", email="a@e.com"))
    repo.save(User(id="u2", name="Bob", email="b@e.com"))
    all_users = repo.find_all()
    assert len(all_users) == 2


def test_delete():
    repo = InMemoryRepository()
    repo.save(User(id="u1", name="Alice", email="a@e.com"))
    repo.delete("u1")
    assert repo.find_by_id("u1") is None


def test_service_result_ok():
    result = ServiceResult.ok(data={"id": 1})
    assert result.success is True
    assert result.data == {"id": 1}


def test_service_result_fail():
    result = ServiceResult.fail("Not found")
    assert result.success is False
    assert result.error == "Not found"
