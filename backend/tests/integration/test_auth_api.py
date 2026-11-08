"""Login, identity, session lifetime and logout over HTTP (spec 0002, AC-1..AC-6, AC-8)."""

import hashlib
import logging
import sqlite3
from datetime import timedelta
from pathlib import Path

import pytest
from conftest import PASSWORD, START, AuthApp, ClientFactory
from fastapi.testclient import TestClient

from app.domain.auth import Role
from app.main import create_app

pytestmark = pytest.mark.integration


def login(app: AuthApp, username: str, password: str = PASSWORD):  # type: ignore[no-untyped-def]
    return app.client.post("/api/auth/login", json={"username": username, "password": password})


def test_login_then_me_returns_display_name_and_role(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)", Role.MANAGER)

    response = login(auth_app, "mert.yilmaz")
    me = auth_app.client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"display_name": "Mert Yılmaz (demo)", "role": "MANAGER"}
    assert me.status_code == 200
    assert me.json() == {"display_name": "Mert Yılmaz (demo)", "role": "MANAGER"}


def test_session_cookie_is_http_only_and_strict(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")

    cookie = login(auth_app, "mert.yilmaz").headers["set-cookie"].lower()

    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "max-age=28800" in cookie


def test_login_accepts_username_in_other_case(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")

    assert login(auth_app, "Mert.YILMAZ").status_code == 200


def test_wrong_password_and_unknown_user_get_identical_response(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")

    wrong_password = login(auth_app, "mert.yilmaz", "parola-124")
    unknown_user = login(auth_app, "kimse.yok")

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
    assert wrong_password.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert wrong_password.json()["error"]["message"] == "Kullanıcı adı veya parola hatalı."
    assert "set-cookie" not in wrong_password.headers
    assert auth_app.client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("", PASSWORD),
        ("ab", PASSWORD),
        ("a" * 33, PASSWORD),
        ("mert yilmaz", PASSWORD),
        ("mert@yilmaz", PASSWORD),
        ("mert.yilmaz", ""),
        ("mert.yilmaz", "a" * 4),
        ("mert.yilmaz", "a" * 129),
    ],
)
def test_login_rejects_malformed_input(auth_app: AuthApp, username: str, password: str) -> None:
    response = login(auth_app, username, password)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INPUT"
    assert "set-cookie" not in response.headers


def test_login_rejects_missing_fields_without_echoing_input(auth_app: AuthApp) -> None:
    response = auth_app.client.post("/api/auth/login", json={"password": "sir-parola-77"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INPUT"
    assert "sir-parola-77" not in response.text


@pytest.mark.parametrize(
    ("username", "password"),
    [("abc", PASSWORD), ("a" * 32, PASSWORD), ("abc", "a" * 5), ("abc", "a" * 128)],
)
def test_login_accepts_boundary_lengths(auth_app: AuthApp, username: str, password: str) -> None:
    auth_app.add_user(username, "Sınır Kullanıcı (demo)", password=password)

    assert login(auth_app, username, password).status_code == 200


def test_me_with_expired_session_reports_session_expired(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    login(auth_app, "mert.yilmaz")

    auth_app.clock.current = START + timedelta(hours=8) - timedelta(seconds=1)
    still_valid = auth_app.client.get("/api/auth/me")
    auth_app.clock.current = START + timedelta(hours=8)
    expired = auth_app.client.get("/api/auth/me")

    assert still_valid.status_code == 200
    assert expired.status_code == 401
    assert expired.json()["error"] == {
        "code": "SESSION_EXPIRED",
        "message": "Oturumunuz sona erdi.",
    }


def test_logout_ends_only_current_session(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    other_browser = auth_app.new_client()
    login(auth_app, "mert.yilmaz")
    other_browser.post("/api/auth/login", json={"username": "mert.yilmaz", "password": PASSWORD})
    stolen_token = auth_app.client.cookies.get("session")

    logout = auth_app.client.post("/api/auth/logout", json={})

    assert logout.status_code == 204
    assert auth_app.client.get("/api/auth/me").status_code == 401
    other_browser.cookies.set("session", stolen_token or "")
    replay = other_browser.get("/api/auth/me")
    assert replay.status_code == 401  # the ended token stays dead, even from elsewhere
    other_browser.cookies.clear()
    other_browser.post("/api/auth/login", json={"username": "mert.yilmaz", "password": PASSWORD})
    assert other_browser.get("/api/auth/me").status_code == 200
    other_browser.close()


def test_auth_responses_and_logs_contain_no_secrets(
    auth_app: AuthApp, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    with auth_app.database.connect() as connection:
        (stored_hash,) = connection.execute(
            "SELECT password_hash FROM employees WHERE username = 'mert.yilmaz'"
        ).fetchone()

    responses = [
        login(auth_app, "mert.yilmaz", "parola-124"),
        login(auth_app, "mert.yilmaz"),
    ]
    token = auth_app.client.cookies.get("session")
    responses += [
        auth_app.client.get("/api/auth/me"),
        auth_app.client.post("/api/auth/logout", json={}),
    ]

    assert stored_hash != PASSWORD and PASSWORD not in stored_hash
    for response in responses:
        # The cookie is the token's only carrier (docs/security.md); everywhere else, nothing.
        visible = response.text + str(
            {k: v for k, v in response.headers.items() if k.lower() != "set-cookie"}
        )
        for secret in (PASSWORD, "parola-124", stored_hash, token or "<no token>"):
            assert secret not in visible
    for secret in (PASSWORD, "parola-124", stored_hash, token or "<no token>"):
        assert secret not in caplog.text


def test_post_without_json_is_rejected(auth_app: AuthApp) -> None:
    response = auth_app.client.post(
        "/api/auth/login",
        content="username=a&password=b",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_session_token_is_stored_only_as_its_hash(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    login(auth_app, "mert.yilmaz")
    token = auth_app.client.cookies.get("session") or ""

    with auth_app.database.connect() as connection:
        stored = [row[0] for row in connection.execute("SELECT token_hash FROM sessions")]

    assert token
    assert stored == [hashlib.sha256(token.encode("utf-8")).hexdigest()]
    assert token not in stored


def test_auth_with_unavailable_database_returns_error_envelope(
    client_for: ClientFactory, tmp_path: Path
) -> None:
    # A directory is not an openable SQLite file: a real sqlite3 error on the auth path.
    response = client_for(str(tmp_path)).post(
        "/api/auth/login", json={"username": "mert.yilmaz", "password": PASSWORD}
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {"code": "DATA_STORE_UNAVAILABLE", "message": "Hizmet şu anda kullanılamıyor."}
    }
    assert str(tmp_path) not in response.text


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_state_changing_methods_without_json_are_rejected(auth_app: AuthApp, method: str) -> None:
    response = auth_app.client.request(
        method, "/api/auth/me", content="x", headers={"Content-Type": "text/plain"}
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_unexpected_error_returns_500_envelope_and_is_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = create_app(":memory:")

    def boom() -> None:
        raise sqlite3.IntegrityError("UNIQUE constraint failed: employees.username")

    app.add_api_route("/boom", boom)
    app.router.routes.insert(0, app.router.routes.pop())  # ahead of the static mount at "/"

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "INTERNAL_ERROR", "message": "Beklenmeyen bir hata oluştu."}
    }
    assert "UNIQUE" not in response.text
    assert any(
        "IntegrityError" in record.getMessage() + (record.exc_text or "")
        or (record.exc_info and record.exc_info[0] is sqlite3.IntegrityError)
        for record in caplog.records
        if record.levelno >= logging.ERROR
    )
