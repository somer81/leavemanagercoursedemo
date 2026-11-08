"""Database: the shared ":memory:" connection serves one transaction at a time (0002 F-4)."""

import logging
import sqlite3
import threading
from pathlib import Path

import pytest

from app.domain.errors import DataStoreUnavailable
from app.repositories.connection import Database

pytestmark = pytest.mark.integration


def test_shared_memory_connection_runs_one_transaction_at_a_time() -> None:
    database = Database(":memory:")
    first_inside = threading.Event()
    release_first = threading.Event()
    second_inside = threading.Event()

    def first() -> None:
        with database.connect():
            first_inside.set()
            release_first.wait(timeout=5)

    def second() -> None:
        first_inside.wait(timeout=5)
        with database.connect():
            second_inside.set()

    threads = [threading.Thread(target=first), threading.Thread(target=second)]
    for thread in threads:
        thread.start()
    first_inside.wait(timeout=5)

    blocked = not second_inside.wait(timeout=0.3)
    release_first.set()
    for thread in threads:
        thread.join(timeout=5)

    assert blocked, "a second transaction entered while the first was still open"
    assert second_inside.is_set()


def test_integrity_error_is_not_masked_as_unavailable() -> None:
    # A constraint violation is a bug or a business rule, not an outage: it must stay visible.
    database = Database(":memory:")
    insert = (
        "INSERT INTO employees (username, display_name, role, password_hash)"
        " VALUES ('ayni', 'Aynı (demo)', 'EMPLOYEE', 'x')"
    )

    with pytest.raises(sqlite3.IntegrityError):
        with database.connect() as connection:
            connection.execute(insert)
            connection.execute(insert)


def test_unavailable_database_is_logged(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    database = Database(str(tmp_path))  # a directory cannot be opened as a database

    with pytest.raises(DataStoreUnavailable):
        with database.connect():
            pass

    errors = [record for record in caplog.records if record.levelno == logging.ERROR]
    assert errors and "OperationalError" in errors[0].getMessage()
