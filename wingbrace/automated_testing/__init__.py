"""
automated_testing
=================
Template classes and helpers for building automated test suites.

Exports:
    BaseTest           -- Base test class with lifecycle hooks and retry logic
    APITestHelper      -- HTTP REST API testing helper
    DataFactory    -- Factory for generating synthetic test data
    PerformanceTest    -- Template for performance and load testing
"""

from wingbrace.automated_testing.base_test import BaseTest
from wingbrace.automated_testing.api_test_helper import APITestHelper
from wingbrace.automated_testing.test_data_factory import DataFactory
from wingbrace.automated_testing.performance_test import PerformanceTest

__all__ = ["BaseTest", "APITestHelper", "DataFactory", "PerformanceTest"]
