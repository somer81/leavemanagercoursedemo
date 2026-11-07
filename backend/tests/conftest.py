from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

ClientFactory = Callable[[str], TestClient]


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
