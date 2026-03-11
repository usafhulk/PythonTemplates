# Wingbrace Python Templates

Reusable Python template modules for **QA Engineering** at Wingbrace.
Inherit from these base classes or call the helper utilities in any project to get
production-ready automated testing, data cleanup, and data analytics out of the box.

> **Zero mandatory external dependencies** — the entire library works with the Python
> standard library.  Optional extras (YAML config, Excel I/O) are installed separately.

---

## Table of Contents

- [Package Structure](#package-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [automated\_testing](#automated_testing)
  - [data\_cleanup](#data_cleanup)
  - [data\_analytics](#data_analytics)
  - [utilities](#utilities)
- [Running the Tests](#running-the-tests)
- [Module Reference](#module-reference)

---

## Package Structure

```
wingbrace/
├── automated_testing/
│   ├── base_test.py          # Base test class with lifecycle hooks & retry
│   ├── api_test_helper.py    # HTTP REST API testing helper
│   ├── test_data_factory.py  # Synthetic test-data generator
│   └── performance_test.py   # Performance / load-testing template
├── data_cleanup/
│   ├── data_cleaner.py       # Missing values, duplicates, type coercion
│   ├── data_validator.py     # Schema & constraint validation
│   └── data_transformer.py   # Normalisation, encoding, reshaping
├── data_analytics/
│   ├── data_analyzer.py      # Descriptive stats, correlation, grouping
│   ├── report_generator.py   # HTML / JSON / CSV report builder
│   └── anomaly_detector.py   # Z-score, IQR, MAD, isolation-score
└── utilities/
    ├── logger.py             # Structured rotating-file logger
    ├── config_manager.py     # JSON / YAML / .env / env-var config loader
    ├── file_handler.py       # CSV, JSON, JSONL, text, Excel I/O
    └── database_helper.py    # SQLite + DB-API 2.0 query helper
```

---

## Installation

```bash
# From the repo root — installs the package in editable mode
pip install -e .

# With all optional extras
pip install -e ".[full]"

# Development (includes pytest)
pip install -e ".[dev]"
```

---

## Quick Start

### automated\_testing

#### Inherit `BaseTest` for structured test classes

```python
from wingbrace.automated_testing import BaseTest

class LoginTest(BaseTest):
    MAX_RETRIES = 2          # retry flaky tests up to 2 extra times
    RETRY_DELAY = 0.5

    def setup(self):
        super().setup()
        # initialise your system under test here
        self.client = MyAppClient()

    def teardown(self):
        self.client.logout()
        super().teardown()

    def test_valid_login(self):
        result = self.client.login("alice", "correct_password")
        self.assert_equal(result.status, "success", "Login should succeed")
        self.assert_not_none(result.token, "Token must be returned")

    def test_invalid_login(self):
        result = self.client.login("alice", "wrong")
        self.assert_equal(result.status, "error")
```

#### `APITestHelper` — REST API testing

```python
from wingbrace.automated_testing import APITestHelper, BaseTest

class UserAPITest(BaseTest):
    def setup(self):
        super().setup()
        self.api = APITestHelper(
            base_url="https://api.example.com/v1",
            default_headers={"Accept": "application/json"},
        )
        self.api.set_bearer_token("my-jwt-token")

    def test_list_users(self):
        response = self.api.get("/users", params={"page": 1})
        self.api.assert_status(response, 200)
        self.api.assert_response_time(response, max_seconds=2.0)
        users = response.json()
        self.assertIsInstance(users, list)

    def test_create_user(self):
        response = self.api.post("/users", body={"name": "Bob", "email": "bob@example.com"})
        self.api.assert_status(response, 201)
```

#### `DataFactory` — synthetic test data

```python
from wingbrace.automated_testing import DataFactory

factory = DataFactory(seed=42)   # reproducible

user    = factory.user()
product = factory.product()
tx      = factory.transaction()

# Bulk generation
users = factory.bulk(factory.user, count=100)

print(user["email"])     # alice.smith@example.com
print(product["sku"])    # ABCD1234
```

#### `PerformanceTest` — latency & throughput

```python
from wingbrace.automated_testing import PerformanceTest

def call_search_api():
    # your API call here
    ...

perf = PerformanceTest(name="Search API")
results = perf.run(call_search_api, iterations=500, concurrency=10, warmup=10)

print(results.summary())
results.assert_p95_under(0.5)   # p95 latency < 500 ms
results.assert_error_rate_below(0.01)  # < 1% errors
```

---

### data\_cleanup

#### `DataCleaner` — fluent data cleaning

```python
from wingbrace.data_cleanup import DataCleaner

raw = [
    {"name": "  Alice ", "age": "29", "score": None,    "city": "NY"},
    {"name": "Bob",       "age": "NaN", "score": "88.5", "city": "LA"},
    {"name": "  Alice ", "age": "29",  "score": None,    "city": "ny"},  # duplicate
]

clean = (
    DataCleaner(raw)
    .strip_whitespace(fields=["name"])
    .fill_missing(0, fields=["score"])
    .coerce_types({"age": int, "score": float})
    .normalise_case("upper", fields=["city"])
    .drop_duplicates()
    .get()
)
```

#### `DataValidator` — schema validation

```python
from wingbrace.data_cleanup import DataValidator

schema = {
    "name":  {"type": str, "required": True, "min_length": 1, "max_length": 100},
    "age":   {"type": int, "required": True, "min_value": 0,  "max_value": 150},
    "email": {"type": str, "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
    "role":  {"type": str, "allowed_values": ["admin", "user", "guest"]},
    "score": {"type": float, "custom": lambda v: 0 <= v <= 100,
              "custom_message": "Score must be 0–100"},
}

result = DataValidator(schema).validate(records)

if not result.is_valid:
    print(result.summary())      # human-readable error list
    for err in result.errors:
        print(err)               # row / field / rule / value / message
```

#### `DataTransformer` — feature engineering

```python
from wingbrace.data_cleanup import DataTransformer

transformed = (
    DataTransformer(records)
    .normalise_minmax(fields=["score", "salary"])
    .one_hot_encode("department", prefix="dept")
    .bin("age", bins=[0, 18, 30, 65, 120], labels=["teen", "young", "adult", "senior"])
    .extract_date_parts("created_at", parts=["year", "month", "weekday"])
    .flatten("address")
    .add_field("full_name", lambda r: f"{r['first']} {r['last']}")
    .get()
)
```

---

### data\_analytics

#### `DataAnalyzer` — statistics & profiling

```python
from wingbrace.data_analytics import DataAnalyzer

analyzer = DataAnalyzer(records)
print(analyzer.summary())

# Field-level statistics
profile = analyzer.profile()
print(profile["salary"])   # mean, median, stdev, min, max, q1, q3, p95 …

# Correlation
r = analyzer.correlation("age", "salary")
matrix = analyzer.correlation_matrix()

# Group aggregation
avg_salary_by_dept = analyzer.group_by("department", "salary", func="mean")

# Frequency table & histogram
freq = analyzer.frequency_table("status", top_n=5)
hist = analyzer.histogram("response_time_ms", bins=20)
```

#### `ReportGenerator` — multi-format reports

```python
from wingbrace.data_analytics import ReportGenerator

report = ReportGenerator(title="Daily QA Report", author="Automated Suite")

report.add_metric("Total Tests", 500, status="ok")
report.add_metric("Pass Rate",  "98.4%", status="ok")
report.add_metric("Open Bugs",  12, status="warn")

report.add_section("Test Summary", {
    "total": 500, "passed": 492, "failed": 8, "skipped": 0
})

report.add_table(
    "Failed Tests",
    headers=["Test ID", "Name", "Error", "Duration"],
    rows=[["T001", "Login timeout", "AssertionError", "3.2s"]],
)

report.add_from_dict_list("Slow Endpoints", slow_endpoints_data)

# Export
report.to_html("reports/daily.html")
report.to_json("reports/daily.json")
report.to_csv("reports/failures.csv")
print(report.to_text())
```

#### `AnomalyDetector` — outlier detection

```python
from wingbrace.data_analytics import AnomalyDetector

detector = AnomalyDetector(metrics_data)

# Z-score
result = detector.zscore(field="response_time_ms", threshold=3.0)

# IQR (Tukey fences)
result = detector.iqr(field="error_count", k=1.5)

# Modified Z-score (robust to existing outliers)
result = detector.modified_zscore(field="cpu_usage", threshold=3.5)

# All fields at once
results = detector.detect_all(["response_time_ms", "memory_mb"], method="iqr")

print(result.summary())
for anomaly in result.anomalies:
    print(anomaly)   # row index, field, value, method, score
```

---

### utilities

#### Logging

```python
from wingbrace.utilities import get_logger

log = get_logger("my_module", level="DEBUG", log_file="logs/app.log")
log.info("Processing %d records", count)
log.warning("Validation failed for row %d", idx)
log.error("Unexpected error: %s", exc)
```

#### Configuration

```python
from wingbrace.utilities import ConfigManager

# From file + environment variable overrides
cfg = ConfigManager.from_json("config/settings.json").with_env_overrides(prefix="APP_")

db_host  = cfg.get("database.host", default="localhost")
db_port  = cfg.get_int("database.port", default=5432)
debug    = cfg.get_bool("debug", default=False)
features = cfg.get_list("feature_flags")

# Required setting (raises KeyError if missing)
api_key  = cfg.require("integrations.api_key")
```

#### File I/O

```python
from wingbrace.utilities import FileHandler

# Read / write CSV
records = FileHandler.read_csv("data/users.csv")
FileHandler.write_csv(clean_records, "output/users_clean.csv")

# Read / write JSON
data = FileHandler.read_json("config/schema.json")
FileHandler.write_json(results, "output/results.json")

# JSONL (streaming / large datasets)
FileHandler.write_jsonl(records, "output/events.jsonl")
rows = FileHandler.read_jsonl("output/events.jsonl")

# List all CSV files recursively
files = FileHandler.list_files("data/", extension=".csv", recursive=True)
```

#### Database

```python
from wingbrace.utilities import DatabaseHelper

# SQLite (built-in, no deps)
with DatabaseHelper.sqlite("qa_results.db") as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS test_runs
        (id TEXT, name TEXT, status TEXT, duration REAL, run_date TEXT)
    """)
    db.bulk_insert("test_runs", test_run_records)
    failed = db.fetchall("SELECT * FROM test_runs WHERE status = ?", ("FAIL",))
    count  = db.fetchscalar("SELECT COUNT(*) FROM test_runs")

# Any DB-API 2.0 driver (PostgreSQL, MySQL, etc.)
import psycopg2
conn = psycopg2.connect(host="localhost", dbname="qa", user="qa", password="secret")
db = DatabaseHelper.from_connection(conn)
rows = db.fetchall("SELECT * FROM test_suites WHERE active = %s", (True,))
```

---

## Running the Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# With coverage report
pytest --cov=wingbrace --cov-report=term-missing

# Run a specific test module
pytest tests/test_data_cleanup.py -v
```

---

## Module Reference

| Module | Class / Function | Purpose |
|--------|-----------------|---------|
| `automated_testing` | `BaseTest` | Base unittest class with lifecycle, retry, logging |
| `automated_testing` | `APITestHelper` | HTTP REST helper — GET/POST/PUT/PATCH/DELETE + assertions |
| `automated_testing` | `DataFactory` | Synthetic users, products, transactions, errors |
| `automated_testing` | `PerformanceTest` | Latency, throughput, error-rate benchmarking |
| `data_cleanup` | `DataCleaner` | Missing values, duplicates, types, ranges |
| `data_cleanup` | `DataValidator` | Schema, type, range, regex, enum, custom rules |
| `data_cleanup` | `DataTransformer` | Min-max/Z-score, one-hot, label, bin, date extraction |
| `data_analytics` | `DataAnalyzer` | Descriptive stats, correlation, group-by, histogram |
| `data_analytics` | `ReportGenerator` | HTML, JSON, CSV, plain-text report builder |
| `data_analytics` | `AnomalyDetector` | Z-score, IQR, modified Z-score, isolation score |
| `utilities` | `get_logger` | Rotating-file structured logger |
| `utilities` | `ConfigManager` | JSON/YAML/.env/env-var layered configuration |
| `utilities` | `FileHandler` | CSV, JSON, JSONL, plain-text, Excel read/write |
| `utilities` | `DatabaseHelper` | SQLite + DB-API 2.0 query/transaction helper |
