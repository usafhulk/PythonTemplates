"""Test Harness Core."""
import logging
import time
import traceback
from typing import Callable, List

from .interfaces import TestCase, TestResult, TestStatus, TestSuiteResult

logger = logging.getLogger(__name__)


class FunctionTestCase(TestCase):
    def __init__(self, name: str, test_fn: Callable[[], None]) -> None:
        self._name = name
        self._test_fn = test_fn

    @property
    def name(self) -> str:
        return self._name

    def run(self) -> TestResult:
        start = time.perf_counter()
        try:
            self._test_fn()
            duration = time.perf_counter() - start
            return TestResult(test_name=self._name, status=TestStatus.PASSED, duration_seconds=duration)
        except AssertionError as e:
            duration = time.perf_counter() - start
            return TestResult(test_name=self._name, status=TestStatus.FAILED,
                             duration_seconds=duration, error_message=str(e))
        except Exception:
            duration = time.perf_counter() - start
            return TestResult(test_name=self._name, status=TestStatus.ERROR,
                             duration_seconds=duration, error_message=traceback.format_exc())


class TestSuite:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tests: List[TestCase] = []

    def add_test(self, test: TestCase) -> "TestSuite":
        self._tests.append(test)
        return self

    def test(self, name: str) -> Callable:
        """Decorator to add test function."""
        def decorator(func: Callable) -> Callable:
            self.add_test(FunctionTestCase(name, func))
            return func
        return decorator

    def run(self) -> TestSuiteResult:
        result = TestSuiteResult(suite_name=self.name)
        for test in self._tests:
            test_result = test.run()
            result.results.append(test_result)
            status_icon = "✓" if test_result.status == TestStatus.PASSED else "✗"
            logger.info("%s %s (%.3fs)", status_icon, test_result.test_name, test_result.duration_seconds)
        logger.info("Suite '%s': %d/%d passed", self.name, result.passed, result.total)
        return result
