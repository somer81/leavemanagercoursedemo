"""People who sign in, and their sessions."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Role(Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class Employee:
    id: int
    username: str
    display_name: str
    role: Role
    manager_id: int | None
    password_hash: str


@dataclass(frozen=True)
class Identity:
    """Who is making a request. Never carries the password hash."""

    id: int
    display_name: str
    role: Role


@dataclass(frozen=True)
class StoredSession:
    token_hash: str
    employee_id: int
    created_at: datetime
