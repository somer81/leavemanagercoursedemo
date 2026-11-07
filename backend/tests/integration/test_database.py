"""Database: the shared ":memory:" connection serves one transaction at a time (0002 F-4)."""

import threading

import pytest

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
