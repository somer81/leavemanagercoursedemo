"""SQLite connections. Every connection goes through here (docs/conventions.md, Known traps)."""

import sqlite3
from collections.abc import Callable

ConnectionFactory = Callable[[], sqlite3.Connection]


def connection_factory(db_path: str) -> ConnectionFactory:
    def connect() -> sqlite3.Connection:
        # check_same_thread=False: TestClient and the server call from worker threads.
        connection = sqlite3.connect(db_path, check_same_thread=False)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    return connect
