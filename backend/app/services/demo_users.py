"""Demo users for the course (spec 0002, R-10). Names are fictitious (docs/domain.md, KVKK)."""

from collections.abc import Sequence
from typing import Protocol

from app.domain.auth import NewEmployee, Role
from app.domain.errors import InvalidInput
from app.services.auth_service import PASSWORD_MAX, PASSWORD_MIN
from app.services.passwords import hash_password

# (username, display name, role, manager username) — managers before their reports.
DEMO_USERS: tuple[tuple[str, str, Role, str | None], ...] = (
    ("admin", "Deniz Aydın (demo)", Role.ADMIN, None),
    ("mert.yilmaz", "Mert Yılmaz (demo)", Role.MANAGER, None),
    ("elif.kaya", "Elif Kaya (demo)", Role.EMPLOYEE, "mert.yilmaz"),
    ("can.demir", "Can Demir (demo)", Role.EMPLOYEE, "mert.yilmaz"),
)


class EmployeeWriter(Protocol):
    def insert_missing(self, employees: Sequence[NewEmployee]) -> None: ...


def create_demo_users(store: EmployeeWriter, password: str | None) -> None:
    """Create the missing demo users; existing ones are left exactly as they are."""
    if password is None or not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        raise InvalidInput()
    store.insert_missing(
        [
            NewEmployee(username, display_name, role, manager, hash_password(password))
            for username, display_name, role, manager in DEMO_USERS
        ]
    )
