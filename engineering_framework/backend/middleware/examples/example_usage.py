"""Middleware Example."""
from engineering_framework.backend.middleware.core import (
    MiddlewarePipeline, LoggingMiddleware, RequestIDMiddleware, CORSMiddleware
)
from engineering_framework.backend.rest_api.interfaces import Request, Response

pipeline = MiddlewarePipeline()
pipeline.add(RequestIDMiddleware())
pipeline.add(LoggingMiddleware())
pipeline.add(CORSMiddleware())

req = Request(method="GET", path="/api/users")
resp = pipeline.execute(req, lambda r: Response(status_code=200, body={"users": []}))
print(resp.status_code, resp.headers)
