"""Employees table (schema.sql). Usernames are stored lower-case."""

import sqlite3
from collections.abc import Sequence

from app.domain.auth import Employee, NewEmployee, Role
from app.repositories.connection import Database


def _employee(row: sqlite3.Row | tuple[object, ...]) -> Employee:
    id_, username, display_name, role, manager_id, password_hash = row
    return Employee(
        id=int(str(id_)),
        username=str(username),
        display_name=str(display_name),
        role=Role(str(role)),
        manager_id=None if manager_id is None else int(str(manager_id)),
        password_hash=str(password_hash),
    )


class SqliteEmployeeRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def find_by_username(self, username: str) -> Employee | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, username, display_name, role, manager_id, password_hash"
                " FROM employees WHERE username = ?",
                (username,),
            ).fetchone()
        return None if row is None else _employee(row)

    def get(self, employee_id: int) -> Employee | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, username, display_name, role, manager_id, password_hash"
                " FROM employees WHERE id = ?",
                (employee_id,),
            ).fetchone()
        return None if row is None else _employee(row)

    def count(self) -> int:
        with self._database.connect() as connection:
            (total,) = connection.execute("SELECT COUNT(*) FROM employees").fetchone()
        return int(total)

    def insert_missing(self, employees: Sequence[NewEmployee]) -> None:
        """Insert the employees whose username is free, in order, in one transaction."""
        with self._database.connect() as connection:
            for new in employees:
                exists = connection.execute(
                    "SELECT 1 FROM employees WHERE username = ?", (new.username,)
                ).fetchone()
                if exists:
                    continue
                manager_id = None
                if new.manager_username is not None:
                    (manager_id,) = connection.execute(
                        "SELECT id FROM employees WHERE username = ?", (new.manager_username,)
                    ).fetchone()
                connection.execute(
                    "INSERT INTO employees"
                    " (username, display_name, role, manager_id, password_hash)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (new.username, new.display_name, new.role.value, manager_id, new.password_hash),
                )
