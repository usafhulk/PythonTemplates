"""REST API Example."""
from engineering_framework.backend.rest_api.core import APIService
from engineering_framework.backend.rest_api.interfaces import Request, Response

api = APIService()

@api.get("/health")
def health(req: Request) -> Response:
    return Response(status_code=200, body={"status": "ok"})

@api.get("/users/{user_id}")
def get_user(req: Request) -> Response:
    return Response(status_code=200, body={"id": req.path_params["user_id"]})

req = Request(method="GET", path="/users/42")
print(api.handle(req))
