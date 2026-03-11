"""Middleware Tests."""
import pytest
from ..core import MiddlewarePipeline, LoggingMiddleware, RequestIDMiddleware, CORSMiddleware
from engineering_framework.backend.rest_api.interfaces import Request, Response


def test_pipeline_executes_handler():
    pipeline = MiddlewarePipeline()
    req = Request(method="GET", path="/test")
    response = pipeline.execute(req, lambda r: Response(status_code=200))
    assert response.status_code == 200


def test_logging_middleware():
    pipeline = MiddlewarePipeline()
    pipeline.add(LoggingMiddleware())
    req = Request(method="GET", path="/test")
    resp = pipeline.execute(req, lambda r: Response(status_code=200))
    assert resp.status_code == 200


def test_request_id_middleware():
    pipeline = MiddlewarePipeline()
    pipeline.add(RequestIDMiddleware())
    req = Request(method="GET", path="/test")
    pipeline.execute(req, lambda r: Response(status_code=200))
    assert "X-Request-ID" in req.headers


def test_cors_middleware():
    pipeline = MiddlewarePipeline()
    pipeline.add(CORSMiddleware(allowed_origins="https://example.com"))
    req = Request(method="GET", path="/test")
    resp = pipeline.execute(req, lambda r: Response(status_code=200))
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://example.com"
