"""Health endpoint through API → service → repository → real SQLite (spec 0001, AC-1..AC-3)."""

from pathlib import Path

import pytest
from conftest import ClientFactory

pytestmark = pytest.mark.integration


def test_health_reports_ok_when_database_reachable(client_for: ClientFactory) -> None:
    response = client_for(":memory:").get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_unavailable_without_internal_details(
    client_for: ClientFactory, tmp_path: Path
) -> None:
    # A directory is not an openable SQLite file: a real sqlite3 error, and nothing is written.
    response = client_for(str(tmp_path)).get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}
    for leak in ("Traceback", "sqlite", "SELECT", str(tmp_path)):
        assert leak not in response.text


def test_health_requires_no_session_and_returns_only_status_fields(
    client_for: ClientFactory,
) -> None:
    client = client_for(":memory:")
    client.cookies.clear()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert set(response.json()) == {"status", "database"}


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_api_documentation_is_not_served_without_session(
    client_for: ClientFactory, path: str
) -> None:
    # Default deny: only login and health are public (docs/security.md).
    response = client_for(":memory:").get(path)

    assert response.status_code == 404


def test_health_reports_unavailable_for_a_file_that_is_not_a_database(
    client_for: ClientFactory, tmp_path: Path
) -> None:
    # SQLite opens lazily: "file is not a database" surfaces on the first statement.
    not_a_database = tmp_path / "leave.db"
    not_a_database.write_bytes(b"this is not an sqlite database file " * 128)

    response = client_for(str(not_a_database)).get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}
    for leak in ("Traceback", "sqlite", "SELECT", str(tmp_path)):
        assert leak not in response.text
