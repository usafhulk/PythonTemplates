"""Mock Service Example."""
from engineering_framework.testing.mock_service.core import InMemoryMockService


class UserService:
    def get_user(self, user_id: int) -> dict:
        raise NotImplementedError("real implementation")


mock_user_service = InMemoryMockService()
mock_user_service.setup_response("get_user", {"id": 1, "name": "Alice", "email": "alice@example.com"})

result = mock_user_service.call("get_user", user_id=1)
print(f"Mock response: {result}")
print(f"Call count: {mock_user_service.call_count('get_user')}")
