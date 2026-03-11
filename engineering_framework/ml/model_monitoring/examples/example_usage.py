"""Model Monitoring Example."""
from engineering_framework.ml.model_monitoring.core import InMemoryModelMonitor

monitor = InMemoryModelMonitor(error_rate_threshold=0.05)
predictions = [1, 0, 1, 1, 0, 1, 0, 1, 1, 1]
ground_truths = [1, 0, 1, 0, 0, 1, 1, 1, 1, 0]

for pred, truth in zip(predictions, ground_truths):
    monitor.record_prediction("classifier_v2", pred, truth)

report = monitor.get_report("classifier_v2")
print(f"Total predictions: {report.total_predictions}")
print(f"Healthy: {report.healthy}")
print(f"Error rate: {report.metrics.get('error_rate', 0):.2%}")
for alert in report.alerts:
    print(f"ALERT: {alert.message}")
