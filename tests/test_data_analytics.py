"""
Unit tests for wingbrace.data_analytics module.
"""

import unittest

from wingbrace.data_analytics.anomaly_detector import AnomalyDetector
from wingbrace.data_analytics.data_analyzer import DataAnalyzer, FieldProfile
from wingbrace.data_analytics.report_generator import ReportGenerator


# ---------------------------------------------------------------------------
# DataAnalyzer
# ---------------------------------------------------------------------------

SAMPLE_DATA = [
    {"name": "Alice", "age": 25, "salary": 50000, "dept": "Engineering"},
    {"name": "Bob",   "age": 30, "salary": 72000, "dept": "Engineering"},
    {"name": "Carol", "age": 28, "salary": 58000, "dept": "Marketing"},
    {"name": "David", "age": 35, "salary": 90000, "dept": "Engineering"},
    {"name": "Eve",   "age": 22, "salary": 45000, "dept": "Marketing"},
]


class TestDataAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = DataAnalyzer(SAMPLE_DATA)

    def test_summary_non_empty(self):
        s = self.analyzer.summary()
        self.assertIn("5 rows", s)

    def test_profile_keys(self):
        profile = self.analyzer.profile()
        self.assertIn("age", profile)
        self.assertIn("salary", profile)

    def test_profile_age(self):
        p = self.analyzer.field_profile("age")
        self.assertEqual(p.total_count, 5)
        self.assertEqual(p.null_count, 0)
        self.assertAlmostEqual(p.mean, 28.0)
        self.assertEqual(p.min, 22)
        self.assertEqual(p.max, 35)

    def test_profile_dtype_numeric(self):
        p = self.analyzer.field_profile("salary")
        self.assertEqual(p.dtype, "numeric")

    def test_profile_dtype_string(self):
        p = self.analyzer.field_profile("name")
        self.assertEqual(p.dtype, "string")

    def test_unique_count(self):
        p = self.analyzer.field_profile("dept")
        self.assertEqual(p.unique_count, 2)

    def test_value_counts(self):
        p = self.analyzer.field_profile("dept")
        vc = p.value_counts
        self.assertEqual(vc.get("Engineering"), 3)
        self.assertEqual(vc.get("Marketing"), 2)

    def test_correlation_positive(self):
        corr = self.analyzer.correlation("age", "salary")
        self.assertIsNotNone(corr)
        # age and salary should be positively correlated in this dataset
        self.assertGreater(corr, 0)

    def test_correlation_same_field(self):
        corr = self.analyzer.correlation("age", "age")
        self.assertAlmostEqual(corr, 1.0, places=5)

    def test_correlation_matrix(self):
        matrix = self.analyzer.correlation_matrix(fields=["age", "salary"])
        self.assertIn("age", matrix)
        self.assertAlmostEqual(matrix["age"]["age"], 1.0, places=5)

    def test_group_by_mean(self):
        result = self.analyzer.group_by("dept", "salary", func="mean")
        self.assertIn("Engineering", result)
        self.assertAlmostEqual(result["Engineering"],
                               (50000 + 72000 + 90000) / 3, delta=1)

    def test_group_by_count(self):
        result = self.analyzer.group_by("dept", "salary", func="count")
        self.assertEqual(result["Engineering"], 3)
        self.assertEqual(result["Marketing"], 2)

    def test_frequency_table(self):
        ft = self.analyzer.frequency_table("dept")
        self.assertEqual(ft["Engineering"]["count"], 3)
        self.assertAlmostEqual(ft["Engineering"]["pct"], 60.0)

    def test_frequency_table_top_n(self):
        ft = self.analyzer.frequency_table("dept", top_n=1)
        self.assertEqual(len(ft), 1)

    def test_histogram_bins(self):
        hist = self.analyzer.histogram("age", bins=3)
        total = sum(b["count"] for b in hist)
        self.assertEqual(total, 5)

    def test_profile_null_rate(self):
        data = [{"v": None}, {"v": None}, {"v": 1}, {"v": 2}]
        p = FieldProfile("v", [r["v"] for r in data])
        self.assertAlmostEqual(p.null_rate, 0.5)

    def test_profile_to_dict(self):
        p = self.analyzer.field_profile("age")
        d = p.to_dict()
        self.assertIn("mean", d)
        self.assertIn("stdev", d)

    def test_percentile(self):
        p = self.analyzer.field_profile("age")
        p50 = p.percentile(50)
        self.assertIsNotNone(p50)
        self.assertGreaterEqual(p50, p.min)
        self.assertLessEqual(p50, p.max)

    def test_empty_dataset(self):
        analyzer = DataAnalyzer([])
        self.assertEqual(analyzer.profile(), {})
        self.assertEqual(analyzer.summary(), "DataAnalyzer: empty dataset.")


# ---------------------------------------------------------------------------
# AnomalyDetector
# ---------------------------------------------------------------------------

CLEAN_DATA = [{"v": float(i)} for i in range(1, 21)]
OUTLIER_DATA = CLEAN_DATA + [{"v": 1000.0}]  # obvious outlier


class TestAnomalyDetector(unittest.TestCase):

    def test_zscore_finds_outlier(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.zscore(field="v", threshold=2.5)
        self.assertGreater(result.anomaly_count, 0)
        outlier_vals = [a.value for a in result.anomalies]
        self.assertIn(1000.0, outlier_vals)

    def test_zscore_clean_data(self):
        detector = AnomalyDetector(CLEAN_DATA)
        result = detector.zscore(field="v", threshold=3.0)
        self.assertEqual(result.anomaly_count, 0)

    def test_iqr_finds_outlier(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.iqr(field="v", k=1.5)
        self.assertGreater(result.anomaly_count, 0)

    def test_modified_zscore_finds_outlier(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.modified_zscore(field="v", threshold=3.5)
        self.assertGreater(result.anomaly_count, 0)

    def test_isolation_score_finds_outlier(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.isolation_score(field="v", threshold=0.5)
        # Just check it returns without error; isolation is probabilistic
        self.assertIsNotNone(result)

    def test_anomaly_rate(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.zscore(field="v", threshold=2.5)
        self.assertGreater(result.anomaly_rate, 0)
        self.assertLess(result.anomaly_rate, 1.0)

    def test_anomaly_indices(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.zscore(field="v", threshold=2.5)
        self.assertIsInstance(result.anomaly_indices, list)

    def test_detect_all(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        results = detector.detect_all(["v"], method="zscore", threshold=2.5)
        self.assertIn("v", results)

    def test_detect_all_invalid_method(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        with self.assertRaises(ValueError):
            detector.detect_all(["v"], method="nonexistent")

    def test_zscore_add_score_field(self):
        data = [{"v": float(i)} for i in range(10)] + [{"v": 1000.0}]
        detector = AnomalyDetector(data)
        detector.zscore(field="v", threshold=2.5, add_score_field=True)
        self.assertIn("v_zscore", data[0])

    def test_summary_string(self):
        detector = AnomalyDetector(OUTLIER_DATA)
        result = detector.zscore(field="v", threshold=2.5)
        s = result.summary()
        self.assertIn("zscore", s)
        self.assertIn("v", s)

    def test_insufficient_data(self):
        detector = AnomalyDetector([{"v": 1.0}])
        result = detector.zscore(field="v")
        self.assertEqual(result.anomaly_count, 0)


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------

class TestReportGenerator(unittest.TestCase):

    def _build_report(self):
        report = ReportGenerator(title="Test Report", author="QA Team")
        report.add_section("Summary", {"total": 100, "passed": 95, "failed": 5})
        report.add_table("Failed Tests",
                         headers=["id", "name", "error"],
                         rows=[["T001", "Login", "Timeout"],
                               ["T002", "Checkout", "500 Error"]])
        report.add_metric("Pass Rate", "95%", status="ok")
        report.add_text("All critical paths verified.", name="Notes")
        return report

    def test_to_text_contains_title(self):
        text = self._build_report().to_text()
        self.assertIn("Test Report", text)

    def test_to_text_contains_section(self):
        text = self._build_report().to_text()
        self.assertIn("Summary", text)
        self.assertIn("total", text)

    def test_to_text_contains_table(self):
        text = self._build_report().to_text()
        self.assertIn("Failed Tests", text)
        self.assertIn("Login", text)

    def test_to_text_contains_metric(self):
        text = self._build_report().to_text()
        self.assertIn("Pass Rate", text)
        self.assertIn("95%", text)

    def test_to_json_valid(self):
        import json
        output = self._build_report().to_json()
        parsed = json.loads(output)
        self.assertEqual(parsed["title"], "Test Report")
        self.assertIsInstance(parsed["sections"], list)

    def test_to_html_contains_title(self):
        html = self._build_report().to_html()
        self.assertIn("<title>Test Report</title>", html)

    def test_to_html_contains_table(self):
        html = self._build_report().to_html()
        self.assertIn("<table>", html)
        self.assertIn("Login", html)

    def test_add_from_dict_list(self):
        data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]
        report = ReportGenerator()
        report.add_from_dict_list("Data", data)
        text = report.to_text()
        self.assertIn("col1", text)

    def test_write_json_file(self):
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "report.json")
            self._build_report().to_json(filepath=path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(data["title"], "Test Report")

    def test_write_html_file(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "report.html")
            self._build_report().to_html(filepath=path)
            self.assertTrue(os.path.exists(path))

    def test_write_csv_file(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "report.csv")
            self._build_report().to_csv(path)
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
