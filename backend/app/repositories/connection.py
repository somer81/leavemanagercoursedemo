"""SQLite access. Every connection goes through Database (docs/conventions.md, Known traps)."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


class Database:
    """Opens connections to one SQLite database and applies the schema on first success.

    ":memory:" is one database per connection, so it keeps a single shared connection.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._shared: sqlite3.Connection | None = None
        self._schema_ready = False

    def _open(self) -> sqlite3.Connection:
        # check_same_thread=False: TestClient and the server call from worker threads.
        connection = sqlite3.connect(self._path, check_same_thread=False)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection; commit on success, roll back on error."""
        if self._path == ":memory:":
            if self._shared is None:
                self._shared = self._open()
            connection = self._shared
        else:
            connection = self._open()
        try:
            if not self._schema_ready:
                connection.executescript(SCHEMA)
                self._schema_ready = True
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            if connection is not self._shared:
                connection.close()
