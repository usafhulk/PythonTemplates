"""
api_test_helper.py
==================
HTTP REST API testing helper for use inside automated test suites.

Provides a thin wrapper around ``urllib.request`` (no third-party deps
required) with convenience methods for common REST verbs, JSON body
handling, authentication headers, and built-in response assertions.

Usage::

    from wingbrace.automated_testing import APITestHelper

    class MyAPITest(BaseTest):
        def setup(self):
            super().setup()
            self.api = APITestHelper(
                base_url="https://api.example.com",
                default_headers={"Accept": "application/json"},
            )

        def test_get_users(self):
            response = self.api.get("/users")
            self.api.assert_status(response, 200)
            data = self.api.json(response)
            self.assertIsInstance(data, list)
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPResponse
from typing import Any

from wingbrace.utilities.logger import get_logger


class APIResponse:
    """Lightweight wrapper around the raw ``http.client.HTTPResponse``."""

    def __init__(
        self,
        status_code: int,
        headers: dict[str, str],
        body: bytes,
        elapsed: float,
        url: str,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.elapsed = elapsed
        self.url = url

    def json(self) -> Any:
        """Decode the response body as JSON."""
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        """Decode the response body as UTF-8 text."""
        return self.body.decode("utf-8")

    def __repr__(self) -> str:
        return (
            f"APIResponse(status={self.status_code}, url={self.url!r}, "
            f"elapsed={self.elapsed:.3f}s, body_len={len(self.body)})"
        )


class APITestHelper:
    """
    Helper for making HTTP requests against a REST API during tests.

    Parameters
    ----------
    base_url:
        Root URL of the API (e.g. ``"https://api.example.com/v1"``).
    default_headers:
        Headers included with every request.
    timeout:
        Request timeout in seconds.
    verify_ssl:
        When *False*, SSL certificate verification is skipped (useful for
        local/self-signed environments).  Defaults to ``True``.
    """

    def __init__(
        self,
        base_url: str = "",
        default_headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers: dict[str, str] = default_headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.log = get_logger(self.__class__.__name__)
        self._session_headers: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------

    def set_bearer_token(self, token: str) -> None:
        """Attach a Bearer token to all subsequent requests."""
        self._session_headers["Authorization"] = f"Bearer {token}"

    def set_basic_auth(self, username: str, password: str) -> None:
        """Attach HTTP Basic auth to all subsequent requests."""
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._session_headers["Authorization"] = f"Basic {credentials}"

    def clear_auth(self) -> None:
        """Remove any stored authentication headers."""
        self._session_headers.pop("Authorization", None)

    # ------------------------------------------------------------------
    # Request methods
    # ------------------------------------------------------------------

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform an HTTP GET request."""
        return self._request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform an HTTP POST request with an optional JSON body."""
        return self._request("POST", path, body=body, headers=headers)

    def put(
        self,
        path: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform an HTTP PUT request with an optional JSON body."""
        return self._request("PUT", path, body=body, headers=headers)

    def patch(
        self,
        path: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform an HTTP PATCH request with an optional JSON body."""
        return self._request("PATCH", path, body=body, headers=headers)

    def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform an HTTP DELETE request."""
        return self._request("DELETE", path, headers=headers)

    # ------------------------------------------------------------------
    # Assertion helpers
    # ------------------------------------------------------------------

    def assert_status(
        self, response: APIResponse, expected: int, message: str = ""
    ) -> None:
        """Assert that *response* has the expected HTTP status code."""
        if response.status_code != expected:
            msg = (
                f"Expected status {expected}, got {response.status_code}. "
                f"{message}  URL: {response.url}"
            )
            self.log.error(msg)
            raise AssertionError(msg)
        self.log.debug(
            "Status assertion passed: %d == %d", response.status_code, expected
        )

    def assert_json_key(
        self, response: APIResponse, key: str, message: str = ""
    ) -> None:
        """Assert that the JSON response body contains *key*."""
        data = response.json()
        if key not in data:
            msg = f"Key {key!r} not found in response JSON. {message}"
            self.log.error(msg)
            raise AssertionError(msg)

    def assert_response_time(
        self, response: APIResponse, max_seconds: float, message: str = ""
    ) -> None:
        """Assert that the response was received within *max_seconds*."""
        if response.elapsed > max_seconds:
            msg = (
                f"Response time {response.elapsed:.3f}s exceeded "
                f"limit {max_seconds}s. {message}"
            )
            self.log.error(msg)
            raise AssertionError(msg)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path
        if params:
            url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
        return url

    def _build_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        merged = {**self.default_headers, **self._session_headers, **(extra or {})}
        return merged

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        url = self._build_url(path, params)
        final_headers = self._build_headers(headers)
        data: bytes | None = None

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            final_headers.setdefault("Content-Type", "application/json")

        req = urllib.request.Request(
            url=url,
            data=data,
            headers=final_headers,
            method=method,
        )

        self.log.debug("%s %s", method, url)

        if not self.verify_ssl:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ctx)
            )
        else:
            opener = urllib.request.build_opener()

        start = time.monotonic()
        try:
            with opener.open(req, timeout=self.timeout) as resp:  # type: ignore[arg-type]
                elapsed = time.monotonic() - start
                raw_body = resp.read()
                resp_headers = dict(resp.headers)
                return APIResponse(
                    status_code=resp.status,
                    headers=resp_headers,
                    body=raw_body,
                    elapsed=elapsed,
                    url=url,
                )
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - start
            raw_body = exc.read() if exc.fp else b""
            self.log.warning(
                "HTTPError %d for %s %s", exc.code, method, url
            )
            return APIResponse(
                status_code=exc.code,
                headers=dict(exc.headers),
                body=raw_body,
                elapsed=elapsed,
                url=url,
            )
        except urllib.error.URLError as exc:
            self.log.error("URLError for %s %s: %s", method, url, exc.reason)
            raise
