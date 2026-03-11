"""
database_helper.py
==================
Database connection and query helper template.

Provides a thin, engine-agnostic wrapper over Python's ``sqlite3`` (built-in)
and also exposes an interface compatible with other DB-API 2.0 drivers
(PostgreSQL via ``psycopg2``, MySQL via ``mysql-connector-python``, etc.).

Usage::

    from wingbrace.utilities import DatabaseHelper

    # SQLite (no extra deps)
    db = DatabaseHelper.sqlite(":memory:")
    db.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
    db.execute("INSERT INTO users VALUES (?, ?, ?)", (1, "Alice", "alice@example.com"))
    users = db.fetchall("SELECT * FROM users")
    print(users)
    # [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}]

    db.close()

    # Context manager (auto-close)
    with DatabaseHelper.sqlite("app.db") as db:
        count = db.fetchone("SELECT COUNT(*) AS n FROM users")["n"]
"""

import sqlite3
from typing import Any, Iterator


class DatabaseHelper:
    """
    Wrapper around a DB-API 2.0 database connection.

    Supports transactions, parameterised queries, bulk inserts,
    and context-manager usage.

    Parameters
    ----------
    connection:
        An open DB-API 2.0 connection object.
    auto_commit:
        When ``True``, each ``execute`` call is committed immediately.
        Set to ``False`` to manage transactions manually.
    """

    def __init__(
        self,
        connection: Any,
        auto_commit: bool = True,
    ) -> None:
        self._conn = connection
        self.auto_commit = auto_commit

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def sqlite(
        cls,
        db_path: str = ":memory:",
        auto_commit: bool = True,
        timeout: float = 30.0,
    ) -> "DatabaseHelper":
        """
        Open an SQLite database and return a ``DatabaseHelper``.

        Parameters
        ----------
        db_path:
            Path to the ``.db`` file, or ``":memory:"`` for an in-memory DB.
        auto_commit:
            Commit after every ``execute`` call.
        timeout:
            Busy-timeout in seconds.

        Returns
        -------
        DatabaseHelper
        """
        conn = sqlite3.connect(db_path, timeout=timeout)
        conn.row_factory = sqlite3.Row
        return cls(conn, auto_commit=auto_commit)

    @classmethod
    def from_connection(
        cls, connection: Any, auto_commit: bool = True
    ) -> "DatabaseHelper":
        """
        Wrap an existing DB-API 2.0 connection.

        Use this to connect with ``psycopg2``, ``mysql-connector-python``,
        ``pyodbc``, or any other compatible driver.

        Example (PostgreSQL)::

            import psycopg2
            conn = psycopg2.connect(host="localhost", dbname="qa", user="qa", password="secret")
            db = DatabaseHelper.from_connection(conn)
        """
        return cls(connection, auto_commit=auto_commit)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> None:
        """
        Execute a non-SELECT SQL statement.

        Parameters
        ----------
        sql:
            SQL statement to execute.
        params:
            Optional bound parameters (positional tuple / list, or
            named dict depending on the driver).
        """
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        if self.auto_commit:
            self._conn.commit()
        cursor.close()

    def execute_many(
        self,
        sql: str,
        params_list: list[tuple | list | dict],
    ) -> int:
        """
        Execute *sql* for each set of parameters in *params_list*.

        Parameters
        ----------
        sql:
            Parameterised SQL statement.
        params_list:
            List of parameter tuples/dicts.

        Returns
        -------
        int
            Number of rows affected.
        """
        cursor = self._conn.cursor()
        cursor.executemany(sql, params_list)
        row_count = cursor.rowcount
        if self.auto_commit:
            self._conn.commit()
        cursor.close()
        return row_count

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def fetchall(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a SELECT and return all rows as a list of dicts.

        Returns
        -------
        list of dict
        """
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return [_row_to_dict(row) for row in rows]

    def fetchone(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> dict[str, Any] | None:
        """
        Execute a SELECT and return the first row as a dict, or ``None``.
        """
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        cursor.close()
        return _row_to_dict(row) if row is not None else None

    def fetchscalar(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> Any:
        """
        Execute a SELECT and return the first column of the first row.

        Useful for queries like ``SELECT COUNT(*) FROM …``.
        """
        row = self.fetchone(sql, params)
        if row is None:
            return None
        return next(iter(row.values()))

    def iterate(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
        chunk_size: int = 1000,
    ) -> Iterator[dict[str, Any]]:
        """
        Yield rows one at a time (memory-efficient for large result sets).

        Parameters
        ----------
        chunk_size:
            Number of rows fetched from the DB per batch.
        """
        cursor = self._conn.cursor()
        cursor.execute(sql, params or ())
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
            for row in rows:
                yield _row_to_dict(row)
        cursor.close()

    # ------------------------------------------------------------------
    # Bulk insert helper
    # ------------------------------------------------------------------

    def bulk_insert(
        self,
        table: str,
        records: list[dict[str, Any]],
        ignore_duplicates: bool = False,
    ) -> int:
        """
        Insert a list of dicts into *table*.

        Parameters
        ----------
        table:
            Target table name.
        records:
            Rows to insert; all dicts must have the same keys.
        ignore_duplicates:
            Use ``INSERT OR IGNORE`` (SQLite) to skip duplicate key errors.

        Returns
        -------
        int
            Number of rows inserted.
        """
        if not records:
            return 0
        columns = list(records[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        verb = "INSERT OR IGNORE" if ignore_duplicates else "INSERT"
        sql = f"{verb} INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        params_list = [tuple(r.get(c) for c in columns) for r in records]
        return self.execute_many(sql, params_list)

    # ------------------------------------------------------------------
    # Transaction management
    # ------------------------------------------------------------------

    def begin(self) -> None:
        """Explicitly begin a transaction (only relevant when auto_commit=False)."""
        self._conn.execute("BEGIN")

    def commit(self) -> None:
        """Commit the current transaction."""
        self._conn.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self._conn.rollback()

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def table_exists(self, table: str) -> bool:
        """Return ``True`` if *table* exists in the current database."""
        row = self.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        )
        return row is not None

    def column_names(self, table: str) -> list[str]:
        """Return the column names of *table*."""
        rows = self.fetchall(f"PRAGMA table_info({table})")
        return [r["name"] for r in rows]

    def list_tables(self) -> list[str]:
        """Return names of all tables in the database."""
        rows = self.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [r["name"] for r in rows]

    def row_count(self, table: str) -> int:
        """Return the number of rows in *table*."""
        return self.fetchscalar(f"SELECT COUNT(*) FROM {table}") or 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def __enter__(self) -> "DatabaseHelper":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        self.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a DB-API row (or sqlite3.Row) to a plain dict."""
    if isinstance(row, dict):
        return row
    if hasattr(row, "keys"):
        return dict(row)
    if hasattr(row, "_fields"):  # namedtuple
        return row._asdict()
    return dict(enumerate(row))
