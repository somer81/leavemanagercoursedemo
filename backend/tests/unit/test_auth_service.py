"""AuthService: login, session lifetime, logout (spec 0002, AC-1..AC-5)."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.auth import Employee, Identity, Role, StoredSession
from app.domain.errors import InvalidCredentials, InvalidInput, SessionExpired, Unauthenticated
from app.services.auth_service import AuthService
from app.services.passwords import hash_password

START = datetime(2026, 11, 9, 9, 0, tzinfo=UTC)
PASSWORD = "parola-123"  # noqa: S105 — fictitious test password


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


class FakeEmployees:
    def __init__(self, *employees: Employee) -> None:
        self._by_name = {e.username: e for e in employees}

    def find_by_username(self, username: str) -> Employee | None:
        return self._by_name.get(username)

    def get(self, employee_id: int) -> Employee | None:
        return next((e for e in self._by_name.values() if e.id == employee_id), None)


class FakeSessions:
    def __init__(self) -> None:
        self.rows: dict[str, StoredSession] = {}

    def create(self, session: StoredSession) -> None:
        self.rows[session.token_hash] = session

    def find(self, token_hash: str) -> StoredSession | None:
        return self.rows.get(token_hash)

    def delete(self, token_hash: str) -> None:
        self.rows.pop(token_hash, None)


ELIF = Employee(
    id=3,
    username="elif.kaya",
    display_name="Elif Kaya (demo)",
    role=Role.EMPLOYEE,
    manager_id=2,
    password_hash=hash_password(PASSWORD),
)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(START)


@pytest.fixture
def service(clock: FixedClock) -> AuthService:
    return AuthService(FakeEmployees(ELIF), FakeSessions(), clock)


def test_login_with_valid_credentials_returns_identity(service: AuthService) -> None:
    result = service.login("elif.kaya", PASSWORD)

    assert result.identity == Identity(id=3, display_name="Elif Kaya (demo)", role=Role.EMPLOYEE)
    assert service.authenticate(result.token) == result.identity


def test_login_username_is_case_insensitive(service: AuthService) -> None:
    assert service.login("Elif.KAYA", PASSWORD).identity.id == 3


def test_login_with_wrong_password_raises_invalid_credentials(service: AuthService) -> None:
    with pytest.raises(InvalidCredentials):
        service.login("elif.kaya", "parola-124")
    with pytest.raises(InvalidCredentials):
        service.login("bilinmeyen", PASSWORD)


@pytest.mark.parametrize("username", ["", "ab", "a" * 33, "elif kaya", "elif@kaya"])
def test_login_rejects_malformed_username(service: AuthService, username: str) -> None:
    with pytest.raises(InvalidInput):
        service.login(username, PASSWORD)


@pytest.mark.parametrize("password", ["", "a" * 4, "a" * 129])
def test_login_rejects_malformed_password(service: AuthService, password: str) -> None:
    with pytest.raises(InvalidInput):
        service.login("elif.kaya", password)


def test_session_valid_one_second_before_eight_hours(
    service: AuthService, clock: FixedClock
) -> None:
    token = service.login("elif.kaya", PASSWORD).token
    clock.current = START + timedelta(hours=8) - timedelta(seconds=1)

    assert service.authenticate(token).id == 3


def test_session_expired_at_exactly_eight_hours(service: AuthService, clock: FixedClock) -> None:
    token = service.login("elif.kaya", PASSWORD).token
    clock.current = START + timedelta(hours=8)

    with pytest.raises(SessionExpired):
        service.authenticate(token)
    with pytest.raises(Unauthenticated):  # an expired session is gone for good
        service.authenticate(token)


def test_unknown_token_is_unauthenticated(service: AuthService) -> None:
    with pytest.raises(Unauthenticated):
        service.authenticate("hic-var-olmayan")


def test_logout_ends_only_that_session(service: AuthService) -> None:
    first = service.login("elif.kaya", PASSWORD).token
    second = service.login("elif.kaya", PASSWORD).token

    service.logout(first)

    with pytest.raises(Unauthenticated):
        service.authenticate(first)
    assert service.authenticate(second).id == 3
