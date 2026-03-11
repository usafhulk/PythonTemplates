"""
Unit tests for wingbrace.utilities module.
"""

import json
import os
import tempfile
import unittest

from wingbrace.utilities.config_manager import ConfigManager
from wingbrace.utilities.database_helper import DatabaseHelper
from wingbrace.utilities.file_handler import FileHandler
from wingbrace.utilities.logger import get_logger


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class TestLogger(unittest.TestCase):

    def test_returns_logger(self):
        import logging
        log = get_logger("test_logger_unique1")
        self.assertIsInstance(log, logging.Logger)

    def test_same_name_returns_same_instance(self):
        log1 = get_logger("test_logger_unique2")
        log2 = get_logger("test_logger_unique2")
        self.assertIs(log1, log2)

    def test_logger_has_handlers(self):
        log = get_logger("test_logger_unique3")
        self.assertGreater(len(log.handlers), 0)

    def test_logger_with_file(self):
        with tempfile.TemporaryDirectory() as td:
            log_path = os.path.join(td, "test.log")
            log = get_logger("test_file_logger_abc", log_file=log_path)
            log.info("test message")
            self.assertTrue(os.path.exists(log_path))


# ---------------------------------------------------------------------------
# ConfigManager
# ---------------------------------------------------------------------------

class TestConfigManager(unittest.TestCase):

    def test_from_dict(self):
        cfg = ConfigManager.from_dict({"host": "localhost", "port": 5432})
        self.assertEqual(cfg.get("host"), "localhost")
        self.assertEqual(cfg.get("port"), 5432)

    def test_nested_get(self):
        cfg = ConfigManager.from_dict({"db": {"host": "127.0.0.1", "port": 5432}})
        self.assertEqual(cfg.get("db.host"), "127.0.0.1")
        self.assertEqual(cfg.get("db.port"), 5432)

    def test_get_default(self):
        cfg = ConfigManager.from_dict({})
        self.assertEqual(cfg.get("missing.key", default="fallback"), "fallback")

    def test_get_int(self):
        cfg = ConfigManager.from_dict({"timeout": "30"})
        self.assertEqual(cfg.get_int("timeout"), 30)

    def test_get_float(self):
        cfg = ConfigManager.from_dict({"threshold": "0.95"})
        self.assertAlmostEqual(cfg.get_float("threshold"), 0.95)

    def test_get_bool_true_values(self):
        for val in ("1", "true", "yes", "on", True):
            cfg = ConfigManager.from_dict({"flag": val})
            self.assertTrue(cfg.get_bool("flag"), f"Expected True for {val!r}")

    def test_get_bool_false_values(self):
        for val in ("0", "false", "no", "off", False):
            cfg = ConfigManager.from_dict({"flag": val})
            self.assertFalse(cfg.get_bool("flag"), f"Expected False for {val!r}")

    def test_get_list_from_list(self):
        cfg = ConfigManager.from_dict({"items": [1, 2, 3]})
        self.assertEqual(cfg.get_list("items"), [1, 2, 3])

    def test_get_list_from_string(self):
        cfg = ConfigManager.from_dict({"items": "a,b,c"})
        self.assertEqual(cfg.get_list("items"), ["a", "b", "c"])

    def test_require_existing(self):
        cfg = ConfigManager.from_dict({"key": "value"})
        self.assertEqual(cfg.require("key"), "value")

    def test_require_missing(self):
        cfg = ConfigManager.from_dict({})
        with self.assertRaises(KeyError):
            cfg.require("missing_key")

    def test_set(self):
        cfg = ConfigManager.from_dict({})
        cfg.set("a.b.c", 42)
        self.assertEqual(cfg.get("a.b.c"), 42)

    def test_from_json_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "config.json")
            data = {"env": "test", "debug": True, "db": {"host": "localhost"}}
            with open(path, "w") as f:
                json.dump(data, f)
            cfg = ConfigManager.from_json(path)
            self.assertEqual(cfg.get("env"), "test")
            self.assertEqual(cfg.get("db.host"), "localhost")

    def test_from_dotenv(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, ".env")
            with open(path, "w") as f:
                f.write("# comment\nDB_HOST=localhost\nDB_PORT=5432\n")
            cfg = ConfigManager.from_dotenv(path)
            self.assertEqual(cfg.get("DB_HOST"), "localhost")
            self.assertEqual(cfg.get("DB_PORT"), "5432")

    def test_merge(self):
        base = ConfigManager.from_dict({"a": 1, "b": 2})
        override = ConfigManager.from_dict({"b": 99, "c": 3})
        merged = base.merge(override)
        self.assertEqual(merged.get("a"), 1)
        self.assertEqual(merged.get("b"), 99)
        self.assertEqual(merged.get("c"), 3)

    def test_get_section(self):
        cfg = ConfigManager.from_dict({"db": {"host": "h", "port": 5432}})
        section = cfg.get_section("db")
        self.assertEqual(section.get("host"), "h")

    def test_to_json(self):
        cfg = ConfigManager.from_dict({"key": "val"})
        output = cfg.to_json()
        parsed = json.loads(output)
        self.assertEqual(parsed["key"], "val")

    def test_with_env_overrides(self):
        os.environ["_WINGBRACE_TEST_KEY"] = "env_value"
        try:
            cfg = ConfigManager.from_dict({"_wingbrace_test_key": "file_value"})
            merged = cfg.with_env_overrides(prefix="_WINGBRACE_")
            self.assertEqual(merged.get("test_key"), "env_value")
        finally:
            del os.environ["_WINGBRACE_TEST_KEY"]


# ---------------------------------------------------------------------------
# FileHandler
# ---------------------------------------------------------------------------

class TestFileHandler(unittest.TestCase):

    SAMPLE_DATA = [
        {"id": "1", "name": "Alice", "score": "95.0"},
        {"id": "2", "name": "Bob",   "score": "88.0"},
    ]

    def test_write_and_read_csv(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.csv")
            FileHandler.write_csv(self.SAMPLE_DATA, path)
            rows = FileHandler.read_csv(path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["name"], "Alice")

    def test_append_csv(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.csv")
            FileHandler.write_csv(self.SAMPLE_DATA, path)
            new_row = [{"id": "3", "name": "Carol", "score": "75.0"}]
            FileHandler.append_csv(new_row, path)
            rows = FileHandler.read_csv(path)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[2]["name"], "Carol")

    def test_write_and_read_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.json")
            FileHandler.write_json(self.SAMPLE_DATA, path)
            loaded = FileHandler.read_json(path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[1]["name"], "Bob")

    def test_write_and_read_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.jsonl")
            FileHandler.write_jsonl(self.SAMPLE_DATA, path)
            loaded = FileHandler.read_jsonl(path)
            self.assertEqual(len(loaded), 2)

    def test_append_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.jsonl")
            FileHandler.write_jsonl(self.SAMPLE_DATA, path)
            FileHandler.write_jsonl([{"id": "3", "name": "Carol"}], path, append=True)
            loaded = FileHandler.read_jsonl(path)
            self.assertEqual(len(loaded), 3)

    def test_write_and_read_text(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "notes.txt")
            FileHandler.write_text("Hello World\nLine 2", path)
            content = FileHandler.read_text(path)
            self.assertIn("Hello World", content)

    def test_read_lines(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "lines.txt")
            FileHandler.write_text("line1\nline2\n\nline3\n", path)
            lines = FileHandler.read_lines(path, skip_blank=True)
            self.assertEqual(len(lines), 3)

    def test_csv_to_string(self):
        output = FileHandler.csv_to_string(self.SAMPLE_DATA)
        self.assertIn("Alice", output)
        self.assertIn("name", output)

    def test_file_exists_true(self):
        with tempfile.NamedTemporaryFile() as f:
            self.assertTrue(FileHandler.file_exists(f.name))

    def test_file_exists_false(self):
        self.assertFalse(FileHandler.file_exists("/nonexistent/path.txt"))

    def test_ensure_dir(self):
        with tempfile.TemporaryDirectory() as td:
            new_dir = os.path.join(td, "sub", "dir")
            result = FileHandler.ensure_dir(new_dir)
            self.assertTrue(os.path.isdir(result))

    def test_list_files(self):
        with tempfile.TemporaryDirectory() as td:
            for name in ["a.csv", "b.csv", "c.json"]:
                FileHandler.write_text("", os.path.join(td, name))
            csv_files = FileHandler.list_files(td, extension=".csv")
            self.assertEqual(len(csv_files), 2)

    def test_list_files_recursive(self):
        with tempfile.TemporaryDirectory() as td:
            sub = os.path.join(td, "sub")
            os.makedirs(sub)
            FileHandler.write_text("", os.path.join(td, "root.txt"))
            FileHandler.write_text("", os.path.join(sub, "child.txt"))
            files = FileHandler.list_files(td, recursive=True)
            self.assertEqual(len(files), 2)


# ---------------------------------------------------------------------------
# DatabaseHelper
# ---------------------------------------------------------------------------

class TestDatabaseHelper(unittest.TestCase):

    def _make_db(self):
        db = DatabaseHelper.sqlite(":memory:")
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
        )
        return db

    def test_execute_and_fetchall(self):
        with self._make_db() as db:
            db.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
            db.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
            rows = db.fetchall("SELECT * FROM users ORDER BY id")
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["name"], "Alice")

    def test_fetchone(self):
        with self._make_db() as db:
            db.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
            row = db.fetchone("SELECT * FROM users WHERE id = ?", (1,))
            self.assertIsNotNone(row)
            self.assertEqual(row["name"], "Alice")

    def test_fetchone_missing(self):
        with self._make_db() as db:
            row = db.fetchone("SELECT * FROM users WHERE id = ?", (999,))
            self.assertIsNone(row)

    def test_fetchscalar(self):
        with self._make_db() as db:
            db.execute("INSERT INTO users VALUES (1, 'Alice', 'a@x.com')")
            db.execute("INSERT INTO users VALUES (2, 'Bob', 'b@x.com')")
            count = db.fetchscalar("SELECT COUNT(*) FROM users")
            self.assertEqual(count, 2)

    def test_execute_many(self):
        with self._make_db() as db:
            params = [(i, f"User{i}", f"user{i}@x.com") for i in range(1, 6)]
            affected = db.execute_many(
                "INSERT INTO users VALUES (?, ?, ?)", params
            )
            self.assertEqual(db.row_count("users"), 5)

    def test_bulk_insert(self):
        with self._make_db() as db:
            records = [{"id": i, "name": f"U{i}", "email": f"u{i}@x.com"}
                       for i in range(1, 4)]
            db.bulk_insert("users", records)
            self.assertEqual(db.row_count("users"), 3)

    def test_table_exists(self):
        with self._make_db() as db:
            self.assertTrue(db.table_exists("users"))
            self.assertFalse(db.table_exists("nonexistent"))

    def test_column_names(self):
        with self._make_db() as db:
            cols = db.column_names("users")
            self.assertIn("name", cols)
            self.assertIn("email", cols)

    def test_list_tables(self):
        with self._make_db() as db:
            tables = db.list_tables()
            self.assertIn("users", tables)

    def test_iterate(self):
        with self._make_db() as db:
            params = [(i, f"User{i}", f"u{i}@x.com") for i in range(1, 11)]
            db.execute_many("INSERT INTO users VALUES (?, ?, ?)", params)
            collected = list(db.iterate("SELECT * FROM users", chunk_size=3))
            self.assertEqual(len(collected), 10)

    def test_rollback(self):
        db = DatabaseHelper.sqlite(":memory:", auto_commit=False)
        db.execute("CREATE TABLE t (v INTEGER)")
        db.execute("INSERT INTO t VALUES (1)")
        db.rollback()
        # After rollback the insert should be undone
        rows = db.fetchall("SELECT * FROM t")
        self.assertEqual(len(rows), 0)
        db.close()

    def test_context_manager(self):
        with DatabaseHelper.sqlite(":memory:") as db:
            db.execute("CREATE TABLE t (v TEXT)")
            db.execute("INSERT INTO t VALUES ('hello')")
            row = db.fetchone("SELECT * FROM t")
            self.assertEqual(row["v"], "hello")

    def test_bulk_insert_ignore_duplicates(self):
        with self._make_db() as db:
            db.bulk_insert("users", [{"id": 1, "name": "A", "email": "a@x.com"}])
            # duplicate insert with ignore_duplicates=True should not raise
            db.bulk_insert("users",
                           [{"id": 1, "name": "A", "email": "a@x.com"}],
                           ignore_duplicates=True)
            self.assertEqual(db.row_count("users"), 1)


if __name__ == "__main__":
    unittest.main()
