"""
base_test.py
============
Base test class template for automated test suites.

Provides:
    - Structured setup and teardown lifecycle hooks
    - Built-in retry logic for flaky tests
    - Integrated logging per test
    - Test metadata (name, start time, duration, pass/fail)
    - Screenshot / artefact capture hooks (override in subclasses)

Usage::

    from wingbrace.automated_testing import BaseTest

    class MyFeatureTest(BaseTest):
        def setup(self):
            super().setup()
            # initialise your system under test here

        def test_login_success(self):
            self.log.info("Testing successful login flow")
            # ... your assertions ...
            self.assert_equal(result, expected, "Login should succeed")

        def teardown(self):
            # cleanup resources
            super().teardown()
"""

import time
import traceback
import unittest
from typing import Any, Callable

from wingbrace.utilities.logger import get_logger


class BaseTest(unittest.TestCase):
    """
    Base class for all automated tests at Wingbrace.

    Inherit from this class to gain structured logging, lifecycle hooks,
    retry logic, and helper assertions.  Override ``setup`` and ``teardown``
    rather than ``setUp`` / ``tearDown`` so that the base implementation runs
    reliably.
    """

    #: Number of times a test will be retried on failure before giving up.
    MAX_RETRIES: int = 0

    #: Seconds to wait between retries.
    RETRY_DELAY: float = 1.0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def setUp(self) -> None:
        self._start_time: float = time.time()
        self._test_name: str = self._testMethodName
        self._test_passed: bool = True
        self.log = get_logger(self.__class__.__name__)
        self.log.info("=== START: %s ===", self._test_name)
        self.setup()

    def tearDown(self) -> None:
        duration = time.time() - self._start_time
        status = "PASS" if self._test_passed else "FAIL"
        self.log.info(
            "=== END: %s | %s | %.3fs ===",
            self._test_name,
            status,
            duration,
        )
        self.teardown()

    def setup(self) -> None:
        """
        Override this method to add custom pre-test setup.

        Always call ``super().setup()`` at the start of your override.
        """

    def teardown(self) -> None:
        """
        Override this method to add custom post-test teardown.

        Always call ``super().teardown()`` at the end of your override.
        """

    # ------------------------------------------------------------------
    # Retry helper
    # ------------------------------------------------------------------

    def run_with_retry(
        self,
        func: Callable[[], Any],
        max_retries: int | None = None,
        retry_delay: float | None = None,
        expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> Any:
        """
        Execute *func* up to ``max_retries`` additional times on failure.

        Parameters
        ----------
        func:
            Zero-argument callable to execute.
        max_retries:
            Override the class-level ``MAX_RETRIES`` for this call.
        retry_delay:
            Seconds to wait between attempts.
        expected_exceptions:
            Only retry when one of these exception types is raised.

        Returns
        -------
        Any
            The return value of *func* on success.

        Raises
        ------
        Exception
            Re-raises the last exception when all retries are exhausted.
        """
        retries = max_retries if max_retries is not None else self.MAX_RETRIES
        delay = retry_delay if retry_delay is not None else self.RETRY_DELAY
        last_exc: Exception | None = None

        for attempt in range(retries + 1):
            try:
                return func()
            except expected_exceptions as exc:
                last_exc = exc
                if attempt < retries:
                    self.log.warning(
                        "Attempt %d/%d failed: %s – retrying in %.1fs",
                        attempt + 1,
                        retries + 1,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    self.log.error(
                        "All %d attempt(s) failed for %s",
                        retries + 1,
                        func.__name__ if hasattr(func, "__name__") else repr(func),
                    )
        raise last_exc  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Enhanced assertion helpers
    # ------------------------------------------------------------------

    def assert_equal(self, actual: Any, expected: Any, message: str = "") -> None:
        """Assert that *actual* equals *expected*, logging the result."""
        try:
            self.assertEqual(actual, expected, message)
            self.log.debug("ASSERT PASS – %s: %r == %r", message, actual, expected)
        except AssertionError:
            self._test_passed = False
            self.log.error(
                "ASSERT FAIL – %s: expected %r, got %r", message, expected, actual
            )
            raise

    def assert_not_none(self, value: Any, message: str = "") -> None:
        """Assert that *value* is not ``None``."""
        try:
            self.assertIsNotNone(value, message)
            self.log.debug("ASSERT PASS – %s: value is not None", message)
        except AssertionError:
            self._test_passed = False
            self.log.error("ASSERT FAIL – %s: value is None", message)
            raise

    def assert_contains(self, container: Any, member: Any, message: str = "") -> None:
        """Assert that *member* is in *container*."""
        try:
            self.assertIn(member, container, message)
            self.log.debug(
                "ASSERT PASS – %s: %r in container", message, member
            )
        except AssertionError:
            self._test_passed = False
            self.log.error(
                "ASSERT FAIL – %s: %r not found in container", message, member
            )
            raise

    def assert_true(self, expr: Any, message: str = "") -> None:
        """Assert that *expr* is truthy."""
        try:
            self.assertTrue(expr, message)
            self.log.debug("ASSERT PASS – %s", message)
        except AssertionError:
            self._test_passed = False
            self.log.error("ASSERT FAIL – %s: expression is falsy", message)
            raise

    # ------------------------------------------------------------------
    # Artefact hooks (override in subclasses as needed)
    # ------------------------------------------------------------------

    def capture_screenshot(self, name: str = "") -> None:
        """
        Hook for capturing a screenshot on failure.

        Override this in your subclass to integrate with a browser driver
        (e.g. Selenium, Playwright) or another capture mechanism.
        """
        self.log.debug("capture_screenshot called (no-op in BaseTest): %s", name)

    def capture_log_snapshot(self) -> str:
        """
        Return a snapshot of recent log output as a string.

        Override this to attach relevant log lines to test reports.
        """
        return ""
