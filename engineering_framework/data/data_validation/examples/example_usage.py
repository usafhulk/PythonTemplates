"""Data Validation Example."""
from engineering_framework.data.data_validation.core import RuleBasedDataValidator, ColumnRule

validator = RuleBasedDataValidator([
    ColumnRule("id", not_null=True, dtype=int),
    ColumnRule("name", not_null=True),
    ColumnRule("score", min_value=0, max_value=100),
    ColumnRule("status", allowed_values=["active", "inactive"]),
])

records = [
    {"id": 1, "name": "Alice", "score": 95, "status": "active"},
    {"id": 2, "name": None, "score": 110, "status": "banned"},
]

result = validator.validate_dataset(records)
print(f"Passed: {result.passed}")
print(f"Failed: {result.failed_records}/{result.total_records}")
for e in result.errors:
    print(e)
