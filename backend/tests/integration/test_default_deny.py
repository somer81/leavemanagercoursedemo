"""Default deny: every API route needs a session except login and health (spec 0002, AC-7).

Routes are read from the app itself, so a route added later is covered without editing this test.
"""

from datetime import timedelta

import pytest
from conftest import PASSWORD, START, AuthApp

pytestmark = pytest.mark.integration

PUBLIC_API = {("POST", "/api/auth/login"), ("GET", "/api/health")}


def api_routes(app: AuthApp) -> set[tuple[str, str]]:
    # app.openapi() is the public, prefix-aware route listing (it works with openapi_url=None).
    paths = app.client.app.openapi()["paths"]  # type: ignore[attr-defined]
    return {
        (method.upper(), path)
        for path, operations in paths.items()
        if path.startswith("/api/")
        for method in operations
    }


def call(app: AuthApp, method: str, path: str, session: str | None = None) -> int:
    concrete = path.replace("{", "").replace("}", "")  # any path parameter: a dummy value
    app.client.cookies.clear()
    if session is not None:
        app.client.cookies.set("session", session)
    response = app.client.request(method, concrete, json={})
    app.client.cookies.clear()
    return response.status_code


def test_public_api_routes_are_exactly_login_and_health(auth_app: AuthApp) -> None:
    auth_app.client.cookies.clear()
    public = {
        (method, path)
        for method, path in api_routes(auth_app)
        if call(auth_app, method, path) != 401
    }

    assert public == PUBLIC_API


def test_protected_api_routes_reject_requests_without_valid_session(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    auth_app.client.post("/api/auth/login", json={"username": "mert.yilmaz", "password": PASSWORD})
    real = auth_app.client.cookies.get("session") or ""
    auth_app.client.cookies.clear()
    protected = api_routes(auth_app) - PUBLIC_API
    assert protected, "expected at least one protected API route"

    for method, path in sorted(protected):
        assert call(auth_app, method, path) == 401, (method, path, "no session")
        assert call(auth_app, method, path, "uydurma") == 401, (method, path)
    auth_app.clock.current = START + timedelta(hours=8)
    for method, path in sorted(protected):
        assert call(auth_app, method, path, real) == 401, (method, path, "expired")


def test_static_files_are_served_without_session(auth_app: AuthApp) -> None:
    auth_app.client.cookies.clear()

    for path in ("/", "/styles.css", "/js/health-status.js"):
        assert auth_app.client.get(path).status_code == 200, path
