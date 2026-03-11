"""REST API Tests."""
import pytest
from ..core import APIService, SimpleRouter
from ..interfaces import Request, Response


def test_get_route():
    api = APIService()

    @api.get("/users")
    def list_users(req: Request) -> Response:
        return Response(status_code=200, body={"users": []})

    req = Request(method="GET", path="/users")
    resp = api.handle(req)
    assert resp.status_code == 200
    assert resp.body == {"users": []}


def test_path_params():
    api = APIService()

    @api.get("/users/{user_id}")
    def get_user(req: Request) -> Response:
        return Response(status_code=200, body={"id": req.path_params["user_id"]})

    req = Request(method="GET", path="/users/42")
    resp = api.handle(req)
    assert resp.status_code == 200
    assert resp.body["id"] == "42"


def test_404_not_found():
    api = APIService()
    req = Request(method="GET", path="/nonexistent")
    resp = api.handle(req)
    assert resp.status_code == 404


def test_post_route():
    api = APIService()

    @api.post("/users")
    def create_user(req: Request) -> Response:
        return Response(status_code=201, body={"created": True})

    req = Request(method="POST", path="/users", body={"name": "Alice"})
    resp = api.handle(req)
    assert resp.status_code == 201
