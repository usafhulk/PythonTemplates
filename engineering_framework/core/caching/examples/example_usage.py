"""Caching Example."""
from engineering_framework.core.caching.core import InMemoryCache, cached

cache = InMemoryCache()
cache.set("user:42", {"name": "Alice"}, ttl=300)
user = cache.get("user:42")
print(user)

@cached(cache, ttl=60)
def get_data(item_id: int) -> dict:
    return {"id": item_id, "data": "expensive"}

print(get_data(1))
print(get_data(1))  # from cache
