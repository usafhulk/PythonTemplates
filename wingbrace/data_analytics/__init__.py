"""
data_analytics
==============
Template classes for statistical analysis, anomaly detection, and reporting.

Exports:
    DataAnalyzer     -- Descriptive statistics, correlations, distributions
    ReportGenerator  -- Generate HTML, CSV, and JSON reports
    AnomalyDetector  -- Outlier and anomaly detection algorithms
"""

from wingbrace.data_analytics.data_analyzer import DataAnalyzer
from wingbrace.data_analytics.report_generator import ReportGenerator
from wingbrace.data_analytics.anomaly_detector import AnomalyDetector

__all__ = ["DataAnalyzer", "ReportGenerator", "AnomalyDetector"]
