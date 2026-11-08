"""Default deny: every API route needs a session except login and health (spec 0002, AC-7).

Routes are collected from the app's own route tree — not app.openapi(), which hides
include_in_schema=False routes — so a route added later is covered without editing this test.
"""

from collections.abc import Iterable, Iterator
from datetime import timedelta
from typing import Any

import pytest
from conftest import PASSWORD, START, AuthApp
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from starlette.routing import Mount

from app.main import create_app

pytestmark = pytest.mark.integration

PUBLIC_API = {("POST", "/api/auth/login"), ("GET", "/api/health")}


def _walk(routes: Iterable[Any], prefix: str = "") -> Iterator[tuple[str, APIRoute]]:
    """Yield (full path, route). Paths inside an included router omit its include prefix."""
    for route in routes:
        if isinstance(route, APIRoute):
            yield prefix + route.path, route
        elif hasattr(route, "original_router"):  # FastAPI ≥ 0.16x wraps included routers
            context = getattr(route, "include_context", None)
            if context is None or not hasattr(context, "prefix"):
                raise AssertionError("included router without a readable prefix: extend the walk")
            yield from _walk(route.original_router.routes, prefix + context.prefix)
        elif isinstance(route, Mount) and isinstance(route.app, StaticFiles):
            continue  # the public frontend, checked separately below
        else:
            raise AssertionError(f"unknown route type {type(route)!r}: extend the walk")


def api_routes(app: FastAPI) -> set[tuple[str, str]]:
    walked = {
        (method, path)
        for path, route in _walk(app.routes)
        if path.startswith("/api/")
        for method in route.methods
    }
    documented = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
    }
    # A prefix the walk cannot see would show up here as a documented route it missed.
    assert documented <= walked, documented - walked
    return walked


def status_of(client: TestClient, method: str, path: str, session: str | None = None) -> int:
    concrete = path.replace("{", "").replace("}", "")  # any path parameter: a dummy value
    client.cookies.clear()
    if session is not None:
        client.cookies.set("session", session)
    response = client.request(method, concrete, json={})
    client.cookies.clear()
    return response.status_code


def public_routes(client: TestClient) -> set[tuple[str, str]]:
    app = client.app
    assert isinstance(app, FastAPI)
    return {
        (method, path) for method, path in api_routes(app) if status_of(client, method, path) != 401
    }


def test_public_api_routes_are_exactly_login_and_health(auth_app: AuthApp) -> None:
    assert public_routes(auth_app.client) == PUBLIC_API


def test_hidden_unprotected_route_is_detected() -> None:
    # The check above must fail for a route someone forgot to protect and hid from the schema —
    # added directly, or through a router included with a prefix.
    app = create_app(":memory:")
    app.get("/api/hidden", include_in_schema=False)(lambda: {"data": 1})
    router = APIRouter()
    router.get("/secret", include_in_schema=False)(lambda: {"data": 2})
    app.include_router(router, prefix="/api/x")

    with TestClient(app) as client:
        public = public_routes(client)

    assert ("GET", "/api/hidden") in public
    assert ("GET", "/api/x/secret") in public


def test_protected_api_routes_reject_requests_without_valid_session(auth_app: AuthApp) -> None:
    auth_app.add_user("mert.yilmaz", "Mert Yılmaz (demo)")
    auth_app.client.post("/api/auth/login", json={"username": "mert.yilmaz", "password": PASSWORD})
    real = auth_app.client.cookies.get("session") or ""
    app = auth_app.client.app
    assert isinstance(app, FastAPI)
    protected = api_routes(app) - PUBLIC_API
    assert protected, "expected at least one protected API route"

    for method, path in sorted(protected):
        assert status_of(auth_app.client, method, path) == 401, (method, path, "no session")
        assert status_of(auth_app.client, method, path, "uydurma") == 401, (method, path)
    auth_app.clock.current = START + timedelta(hours=8)
    for method, path in sorted(protected):
        assert status_of(auth_app.client, method, path, real) == 401, (method, path, "expired")


def test_static_files_are_served_without_session(auth_app: AuthApp) -> None:
    auth_app.client.cookies.clear()

    for path in ("/", "/styles.css", "/js/health-status.js"):
        assert auth_app.client.get(path).status_code == 200, path
