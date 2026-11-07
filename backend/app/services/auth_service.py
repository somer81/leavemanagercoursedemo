"""Sign-in, session lifetime and sign-out (spec 0002)."""

import hashlib
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from app.domain.auth import Employee, Identity, StoredSession
from app.domain.errors import InvalidCredentials, InvalidInput, SessionExpired, Unauthenticated
from app.services.clock import Clock
from app.services.passwords import DUMMY_HASH, verify_password

SESSION_LIFETIME = timedelta(hours=8)
USERNAME_PATTERN = re.compile(r"[a-z0-9._-]{3,32}")
PASSWORD_MIN, PASSWORD_MAX = 5, 128


class EmployeeStore(Protocol):
    def find_by_username(self, username: str) -> Employee | None: ...

    def get(self, employee_id: int) -> Employee | None: ...


class SessionStore(Protocol):
    def create(self, session: StoredSession) -> None: ...

    def find(self, token_hash: str) -> StoredSession | None: ...

    def delete(self, token_hash: str) -> None: ...


@dataclass(frozen=True)
class LoginResult:
    token: str
    identity: Identity


def token_hash(token: str) -> str:
    """Sessions are stored by the SHA-256 of their token, never the token itself."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def normalize_username(username: str) -> str:
    return username.lower()


def check_formats(username: str, password: str) -> None:
    if not USERNAME_PATTERN.fullmatch(normalize_username(username)):
        raise InvalidInput()
    if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        raise InvalidInput()


def _identity(employee: Employee) -> Identity:
    return Identity(id=employee.id, display_name=employee.display_name, role=employee.role)


class AuthService:
    def __init__(
        self,
        employees: EmployeeStore,
        sessions: SessionStore,
        clock: Clock,
        new_token: Callable[[], str] = lambda: secrets.token_urlsafe(32),
    ) -> None:
        self._employees = employees
        self._sessions = sessions
        self._clock = clock
        self._new_token = new_token

    def login(self, username: str, password: str) -> LoginResult:
        check_formats(username, password)
        employee = self._employees.find_by_username(normalize_username(username))
        if employee is None:
            verify_password(password, DUMMY_HASH)  # same cost as a real check
            raise InvalidCredentials()
        if not verify_password(password, employee.password_hash):
            raise InvalidCredentials()
        token = self._new_token()
        self._sessions.create(
            StoredSession(
                token_hash=token_hash(token), employee_id=employee.id, created_at=self._clock.now()
            )
        )
        return LoginResult(token=token, identity=_identity(employee))

    def authenticate(self, token: str) -> Identity:
        session = self._sessions.find(token_hash(token))
        if session is None:
            raise Unauthenticated()
        if self._clock.now() >= session.created_at + SESSION_LIFETIME:
            self._sessions.delete(session.token_hash)
            raise SessionExpired()
        employee = self._employees.get(session.employee_id)
        if employee is None:
            raise Unauthenticated()
        return _identity(employee)

    def logout(self, token: str) -> None:
        self._sessions.delete(token_hash(token))
