"""API Testing Example."""
from engineering_framework.testing.api_testing.core import MockAPITestClient, APITestAssertions
from engineering_framework.testing.api_testing.interfaces import APITestRequest, APITestResponse

client = MockAPITestClient()
client.register("GET", "/users/1", lambda r: APITestResponse(
    status_code=200, body={"id": 1, "name": "Alice", "email": "alice@example.com"}
))
client.register("POST", "/users", lambda r: APITestResponse(
    status_code=201, body={"id": 2}
))

resp = client.send(APITestRequest(method="GET", path="/users/1"))
APITestAssertions.from_response(resp).status(200).has_key("id").has_key("name").assert_all()
print("All assertions passed!")
