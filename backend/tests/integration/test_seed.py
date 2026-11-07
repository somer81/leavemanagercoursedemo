"""Demo users seed command (spec 0002, AC-9, AC-10). Each test gets its own database file."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.connection import Database
from app.seed import main

pytestmark = pytest.mark.integration

DEMO = "demo-parola"  # noqa: S105 — fictitious demo password
EXPECTED = {
    ("admin", "ADMIN", None),
    ("mert.yilmaz", "MANAGER", None),
    ("elif.kaya", "EMPLOYEE", "mert.yilmaz"),
    ("can.demir", "EMPLOYEE", "mert.yilmaz"),
}


def employees(db_file: Path) -> set[tuple[str, str, str | None]]:
    with Database(str(db_file)).connect() as connection:
        rows = connection.execute(
            "SELECT e.username, e.role, m.username FROM employees e"
            " LEFT JOIN employees m ON m.id = e.manager_id"
        ).fetchall()
    return {(str(u), str(r), None if m is None else str(m)) for u, r, m in rows}


def can_login(db_file: Path, username: str, password: str) -> bool:
    with TestClient(create_app(str(db_file))) as client:
        response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.status_code == 200


def test_seed_creates_demo_users_with_roles_and_manager(tmp_path: Path) -> None:
    db_file = tmp_path / "leave.db"

    code = main({"LEAVE_DB_PATH": str(db_file), "DEMO_PASSWORD": DEMO})

    assert code == 0
    assert employees(db_file) == EXPECTED
    for username, _, _ in EXPECTED:
        assert can_login(db_file, username, DEMO), username


@pytest.mark.parametrize("env_password", [None, "", "abcd"])
def test_seed_without_valid_password_creates_no_users(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], env_password: str | None
) -> None:
    db_file = tmp_path / "leave.db"
    env = {"LEAVE_DB_PATH": str(db_file)}
    if env_password is not None:
        env["DEMO_PASSWORD"] = env_password

    code = main(env)

    assert code == 1
    assert employees(db_file) == set()
    output = capsys.readouterr()
    assert "DEMO_PASSWORD" in output.err
    if env_password:
        assert env_password not in output.out + output.err


def test_seed_accepts_five_character_password(tmp_path: Path) -> None:
    db_file = tmp_path / "leave.db"

    assert main({"LEAVE_DB_PATH": str(db_file), "DEMO_PASSWORD": "abcde"}) == 0
    assert can_login(db_file, "admin", "abcde")


def test_seed_rerun_keeps_existing_users_unchanged(tmp_path: Path) -> None:
    db_file = tmp_path / "leave.db"
    main({"LEAVE_DB_PATH": str(db_file), "DEMO_PASSWORD": DEMO})

    code = main({"LEAVE_DB_PATH": str(db_file), "DEMO_PASSWORD": "baska-parola"})

    assert code == 0
    assert employees(db_file) == EXPECTED
    assert can_login(db_file, "elif.kaya", DEMO)
    assert not can_login(db_file, "elif.kaya", "baska-parola")
