"""Service Layer Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]: ...

    @abstractmethod
    def find_all(self) -> List[T]: ...

    @abstractmethod
    def save(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, id: ID) -> None: ...


class UseCase(ABC, Generic[T]):
    @abstractmethod
    def execute(self, request: Any) -> T: ...
