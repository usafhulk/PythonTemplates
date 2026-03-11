"""API Testing Tests."""
import pytest
from ..core import MockAPITestClient, APITestAssertions
from ..interfaces import APITestRequest, APITestResponse


def test_mock_client_registered_route():
    client = MockAPITestClient()
    client.register("GET", "/health", lambda r: APITestResponse(
        status_code=200, body={"status": "ok"}
    ))
    resp = client.send(APITestRequest(method="GET", path="/health"))
    assert resp.status_code == 200


def test_mock_client_404():
    client = MockAPITestClient()
    resp = client.send(APITestRequest(method="GET", path="/nonexistent"))
    assert resp.status_code == 404


def test_assertions_pass():
    resp = APITestResponse(status_code=200, body={"id": 1, "name": "Alice"})
    APITestAssertions.from_response(resp).status(200).has_key("id").has_key("name").assert_all()


def test_assertions_fail_status():
    resp = APITestResponse(status_code=404, body={})
    with pytest.raises(AssertionError):
        APITestAssertions.from_response(resp).status(200).assert_all()


def test_assertions_fail_key():
    resp = APITestResponse(status_code=200, body={"name": "Alice"})
    with pytest.raises(AssertionError):
        APITestAssertions.from_response(resp).has_key("email").assert_all()
