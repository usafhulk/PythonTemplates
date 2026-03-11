"""
Unit tests for wingbrace.automated_testing module.
"""

import time
import unittest

from wingbrace.automated_testing.api_test_helper import APIResponse, APITestHelper
from wingbrace.automated_testing.base_test import BaseTest
from wingbrace.automated_testing.performance_test import PerformanceResult, PerformanceTest
from wingbrace.automated_testing.test_data_factory import DataFactory


# ---------------------------------------------------------------------------
# DataFactory
# ---------------------------------------------------------------------------

class TestDataFactory(unittest.TestCase):
    def setUp(self):
        self.factory = DataFactory(seed=42)

    def test_uuid_is_string_and_unique(self):
        ids = {self.factory.uuid() for _ in range(20)}
        self.assertEqual(len(ids), 20)

    def test_integer_in_range(self):
        for _ in range(50):
            v = self.factory.integer(10, 20)
            self.assertGreaterEqual(v, 10)
            self.assertLessEqual(v, 20)

    def test_floating_in_range(self):
        for _ in range(50):
            v = self.factory.floating(0.0, 1.0)
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)

    def test_email_format(self):
        email = self.factory.email()
        self.assertIn("@", email)
        self.assertIn(".", email.split("@")[1])

    def test_phone_format(self):
        phone = self.factory.phone()
        parts = phone.split("-")
        self.assertEqual(len(parts), 3)

    def test_user_keys(self):
        user = self.factory.user()
        expected = {"id", "first_name", "last_name", "email", "phone",
                    "address", "date_of_birth", "is_active", "created_at"}
        self.assertTrue(expected.issubset(user.keys()))

    def test_product_keys(self):
        product = self.factory.product()
        self.assertIn("sku", product)
        self.assertIn("price", product)

    def test_transaction_keys(self):
        tx = self.factory.transaction()
        self.assertIn("transaction_id", tx)
        self.assertIn("amount", tx)

    def test_bulk(self):
        users = self.factory.bulk(self.factory.user, count=10)
        self.assertEqual(len(users), 10)
        # All should be dicts
        self.assertTrue(all(isinstance(u, dict) for u in users))

    def test_seeded_reproducibility(self):
        f1 = DataFactory(seed=1)
        f2 = DataFactory(seed=1)
        self.assertEqual(f1.user()["email"], f2.user()["email"])

    def test_address_keys(self):
        addr = self.factory.address()
        self.assertIn("street", addr)
        self.assertIn("zip_code", addr)

    def test_date_between(self):
        from datetime import date
        d = self.factory.date_between(date(2020, 1, 1), date(2020, 12, 31))
        self.assertEqual(d.year, 2020)

    def test_api_error_structure(self):
        err = self.factory.api_error(status_code=404)
        self.assertEqual(err["error"]["code"], 404)


# ---------------------------------------------------------------------------
# BaseTest assertions
# ---------------------------------------------------------------------------

class TestBaseTestAssertions(BaseTest):
    def test_assert_equal_pass(self):
        self.assert_equal(1 + 1, 2, "Basic addition")

    def test_assert_not_none_pass(self):
        self.assert_not_none("value", "Non-null value")

    def test_assert_contains_pass(self):
        self.assert_contains([1, 2, 3], 2, "List contains 2")

    def test_assert_true_pass(self):
        self.assert_true(True, "True is truthy")

    def test_assert_equal_fail(self):
        with self.assertRaises(AssertionError):
            self.assert_equal(1, 2, "Should fail")

    def test_run_with_retry_success(self):
        call_count = [0]

        def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("not yet")

        self.run_with_retry(flaky, max_retries=3, retry_delay=0.01)
        self.assertEqual(call_count[0], 3)

    def test_run_with_retry_exhausted(self):
        def always_fail():
            raise RuntimeError("always")

        with self.assertRaises(RuntimeError):
            self.run_with_retry(always_fail, max_retries=2, retry_delay=0.01)


# ---------------------------------------------------------------------------
# APITestHelper
# ---------------------------------------------------------------------------

class TestAPITestHelper(unittest.TestCase):
    def test_build_url_no_base(self):
        helper = APITestHelper()
        url = helper._build_url("/users")
        self.assertEqual(url, "/users")

    def test_build_url_with_base(self):
        helper = APITestHelper(base_url="https://api.example.com")
        url = helper._build_url("/users")
        self.assertEqual(url, "https://api.example.com/users")

    def test_build_url_with_params(self):
        helper = APITestHelper(base_url="https://api.example.com")
        url = helper._build_url("/users", params={"page": 1, "limit": 10})
        self.assertIn("page=1", url)
        self.assertIn("limit=10", url)

    def test_set_bearer_token(self):
        helper = APITestHelper()
        helper.set_bearer_token("mytoken")
        self.assertEqual(helper._session_headers["Authorization"], "Bearer mytoken")

    def test_set_basic_auth(self):
        helper = APITestHelper()
        helper.set_basic_auth("user", "pass")
        self.assertIn("Basic", helper._session_headers["Authorization"])

    def test_clear_auth(self):
        helper = APITestHelper()
        helper.set_bearer_token("token")
        helper.clear_auth()
        self.assertNotIn("Authorization", helper._session_headers)

    def test_assert_status_pass(self):
        helper = APITestHelper()
        resp = APIResponse(200, {}, b"{}", 0.1, "http://example.com")
        helper.assert_status(resp, 200)

    def test_assert_status_fail(self):
        helper = APITestHelper()
        resp = APIResponse(404, {}, b"{}", 0.1, "http://example.com")
        with self.assertRaises(AssertionError):
            helper.assert_status(resp, 200)

    def test_assert_response_time_pass(self):
        helper = APITestHelper()
        resp = APIResponse(200, {}, b"{}", 0.05, "http://example.com")
        helper.assert_response_time(resp, 1.0)

    def test_assert_response_time_fail(self):
        helper = APITestHelper()
        resp = APIResponse(200, {}, b"{}", 2.0, "http://example.com")
        with self.assertRaises(AssertionError):
            helper.assert_response_time(resp, 1.0)

    def test_api_response_json(self):
        import json
        payload = {"key": "value"}
        body = json.dumps(payload).encode()
        resp = APIResponse(200, {}, body, 0.1, "http://example.com")
        self.assertEqual(resp.json(), payload)

    def test_api_response_text(self):
        resp = APIResponse(200, {}, b"hello", 0.1, "http://example.com")
        self.assertEqual(resp.text(), "hello")


# ---------------------------------------------------------------------------
# PerformanceTest
# ---------------------------------------------------------------------------

class TestPerformanceTest(unittest.TestCase):
    def test_run_basic(self):
        perf = PerformanceTest(name="noop")
        result = perf.run(lambda: None, iterations=20, concurrency=2)
        self.assertEqual(result.total_iterations, 20)
        self.assertGreaterEqual(result.successes, 0)

    def test_error_counting(self):
        perf = PerformanceTest(name="always_fail")
        result = perf.run(lambda: (_ for _ in ()).throw(ValueError("fail")),
                          iterations=5, concurrency=1)
        self.assertEqual(result.failures, 5)
        self.assertEqual(result.successes, 0)

    def test_percentile_calculation(self):
        result = PerformanceResult(
            name="test",
            total_iterations=10,
            successes=10,
            failures=0,
            durations=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )
        self.assertAlmostEqual(result.percentile(50), 0.5, delta=0.15)
        self.assertAlmostEqual(result.percentile(95), 0.9, delta=0.15)

    def test_error_rate(self):
        result = PerformanceResult(
            name="test", total_iterations=10,
            successes=8, failures=2, durations=[0.1] * 8
        )
        self.assertAlmostEqual(result.error_rate, 0.2)

    def test_assert_p95_pass(self):
        result = PerformanceResult(
            name="test", total_iterations=10,
            successes=10, failures=0, durations=[0.1] * 10
        )
        result.assert_p95_under(1.0)  # should not raise

    def test_assert_p95_fail(self):
        result = PerformanceResult(
            name="test", total_iterations=10,
            successes=10, failures=0, durations=[2.0] * 10
        )
        with self.assertRaises(AssertionError):
            result.assert_p95_under(1.0)

    def test_to_dict(self):
        result = PerformanceResult(
            name="test", total_iterations=5,
            successes=5, failures=0, durations=[0.1, 0.2, 0.15, 0.18, 0.12]
        )
        d = result.to_dict()
        self.assertIn("latency", d)
        self.assertIn("throughput_per_sec", d)

    def test_summary_string(self):
        result = PerformanceResult(
            name="test", total_iterations=5,
            successes=5, failures=0, durations=[0.1] * 5
        )
        s = result.summary()
        self.assertIn("test", s)
        self.assertIn("Throughput", s)


if __name__ == "__main__":
    unittest.main()
