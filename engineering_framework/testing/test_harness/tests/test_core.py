"""Test Harness Tests."""
import pytest
from ..core import FunctionTestCase, TestSuite
from ..interfaces import TestStatus


def test_passing_test():
    case = FunctionTestCase("should_pass", lambda: None)
    result = case.run()
    assert result.status == TestStatus.PASSED


def test_failing_test():
    def failing():
        assert False, "expected failure"
    case = FunctionTestCase("should_fail", failing)
    result = case.run()
    assert result.status == TestStatus.FAILED
    assert "expected failure" in result.error_message


def test_error_test():
    def erroring():
        raise RuntimeError("unexpected error")
    case = FunctionTestCase("should_error", erroring)
    result = case.run()
    assert result.status == TestStatus.ERROR


def test_suite_execution():
    suite = TestSuite("my_suite")

    @suite.test("passing_test")
    def test1():
        assert 1 + 1 == 2

    @suite.test("failing_test")
    def test2():
        assert False

    result = suite.run()
    assert result.total == 2
    assert result.passed == 1
    assert result.failed == 1
