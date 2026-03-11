"""Service Layer Example."""
from dataclasses import dataclass
from typing import Optional
from engineering_framework.backend.service_layer.core import InMemoryRepository, ServiceResult

@dataclass
class Product:
    id: Optional[str]
    name: str
    price: float

repo = InMemoryRepository()
product = repo.save(Product(id="p1", name="Widget", price=9.99))
print(repo.find_by_id("p1"))
print(ServiceResult.ok(product))
