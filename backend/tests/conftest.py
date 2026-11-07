from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.domain.auth import NewEmployee, Role
from app.main import create_app
from app.repositories.connection import Database
from app.repositories.employee_repository import SqliteEmployeeRepository
from app.services.passwords import hash_password

ClientFactory = Callable[[str], TestClient]

START = datetime(2026, 11, 9, 9, 0, tzinfo=UTC)
PASSWORD = "parola-123"  # noqa: S105 — fictitious test password


class MutableClock:
    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


@pytest.fixture
def client_for() -> Iterator[ClientFactory]:
    """Build a TestClient for an app bound to the given SQLite path; closed after the test."""
    clients: list[TestClient] = []

    def make(db_path: str) -> TestClient:
        client = TestClient(create_app(db_path))
        clients.append(client)
        return client

    yield make
    for client in clients:
        client.close()


@dataclass
class AuthApp:
    """An app on a fresh in-memory database with a clock the test moves."""

    client: TestClient
    clock: MutableClock
    database: Database

    def add_user(
        self,
        username: str,
        display_name: str,
        role: Role = Role.EMPLOYEE,
        password: str = PASSWORD,
    ) -> None:
        SqliteEmployeeRepository(self.database).insert_missing(
            [NewEmployee(username, display_name, role, None, hash_password(password))]
        )

    def new_client(self) -> TestClient:
        """A second browser: same app, its own cookies."""
        return TestClient(self.client.app)


@pytest.fixture
def auth_app() -> Iterator[AuthApp]:
    database = Database(":memory:")
    clock = MutableClock(START)
    client = TestClient(create_app(":memory:", clock=clock, database=database))
    yield AuthApp(client=client, clock=clock, database=database)
    client.close()
