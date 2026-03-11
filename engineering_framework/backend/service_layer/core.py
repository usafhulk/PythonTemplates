"""Service Layer Core."""
import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .interfaces import Repository, UseCase

logger = logging.getLogger(__name__)

T = TypeVar("T")
ID = TypeVar("ID")


class InMemoryRepository(Repository[T, str]):
    """Generic in-memory repository."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def find_by_id(self, id: str) -> Optional[Any]:
        return self._store.get(id)

    def find_all(self) -> List[Any]:
        return list(self._store.values())

    def save(self, entity: Any) -> Any:
        entity_id = getattr(entity, "id", None) or str(uuid.uuid4())
        if hasattr(entity, "id") and entity.id is None:
            object.__setattr__(entity, "id", entity_id)
        self._store[entity_id] = entity
        logger.debug("Entity saved: %s", entity_id)
        return entity

    def delete(self, id: str) -> None:
        self._store.pop(id, None)
        logger.debug("Entity deleted: %s", id)


class ServiceResult:
    """Wraps use case output with success/failure semantics."""

    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None) -> None:
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: Any = None) -> "ServiceResult":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ServiceResult":
        return cls(success=False, error=error)
