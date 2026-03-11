"""Test Harness Example."""
from engineering_framework.testing.test_harness.core import TestSuite

suite = TestSuite("API Integration Tests")

@suite.test("health_endpoint_returns_200")
def test_health():
    status_code = 200
    assert status_code == 200, f"Expected 200, got {status_code}"

@suite.test("user_creation_works")
def test_create_user():
    user = {"id": 1, "name": "Alice"}
    assert user["name"] == "Alice"

result = suite.run()
print(f"Results: {result.passed}/{result.total} passed")
