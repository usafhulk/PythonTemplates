"""Data Quality Example."""
from engineering_framework.data.data_quality.core import (
    DataQualityMonitor, NullRateCheck, UniquenessCheck
)

monitor = DataQualityMonitor()
monitor.add_check(NullRateCheck("user_id", max_null_rate=0.01))
monitor.add_check(UniquenessCheck("user_id", min_uniqueness=0.99))
monitor.add_check(NullRateCheck("email", max_null_rate=0.05))

data = [{"user_id": i, "email": f"user{i}@example.com"} for i in range(1000)]
report = monitor.run("users_dataset", data)
print(f"Dataset: {report.dataset_name}")
print(f"Overall passed: {report.overall_passed}")
for m in report.metrics:
    print(f"  {m.name}: {m.value:.3f} ({'PASS' if m.passed else 'FAIL'})")
