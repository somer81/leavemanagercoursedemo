"""SQLite access. Every connection goes through Database (docs/conventions.md, Known traps)."""

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path

from app.domain.errors import DataStoreUnavailable

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


class Database:
    """Opens connections to one SQLite database and applies the schema on first success.

    ":memory:" is one database per connection, so it keeps a single shared connection; a lock
    keeps one transaction at a time on it (worker threads would otherwise interleave commits).
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._shared: sqlite3.Connection | None = None
        self._schema_ready = False
        self._lock = threading.RLock()

    def _open(self) -> sqlite3.Connection:
        try:
            # check_same_thread=False: TestClient and the server call from worker threads.
            connection = sqlite3.connect(self._path, check_same_thread=False)
            connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as error:
            raise DataStoreUnavailable() from error
        return connection

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection; commit on success, roll back on error.

        Every sqlite3 error leaves as DataStoreUnavailable, so callers never see driver details.
        """
        if self._path == ":memory:":
            with self._lock:
                if self._shared is None:
                    self._shared = self._open()
                yield from self._transaction(self._shared)
        else:
            yield from self._transaction(self._open())

    def _transaction(self, connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
        try:
            if not self._schema_ready:
                connection.executescript(SCHEMA)
                self._schema_ready = True
            yield connection
            connection.commit()
        except sqlite3.Error as error:
            with suppress(sqlite3.Error):
                connection.rollback()
            raise DataStoreUnavailable() from error
        except BaseException:
            with suppress(sqlite3.Error):
                connection.rollback()
            raise
        finally:
            if connection is not self._shared:
                connection.close()
