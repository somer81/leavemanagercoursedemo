"""Composition root: wires the layers together.

Run: uvicorn --factory app.main:app_from_env --app-dir backend
"""

import os
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth import auth_router, session_dependency
from app.api.errors import install_error_handling
from app.api.health import health_router
from app.repositories.connection import Database
from app.repositories.employee_repository import SqliteEmployeeRepository
from app.repositories.health_repository import SqliteHealthProbe
from app.repositories.session_repository import SqliteSessionRepository
from app.services.auth_service import AuthService
from app.services.clock import Clock
from app.services.health_service import HealthService

# Only the public folder is served; frontend/tests stays private.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public"


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


def create_app(
    db_path: str,
    clock: Clock | None = None,
    database: Database | None = None,
    cookie_secure: bool = False,
) -> FastAPI:
    database = database or Database(db_path)
    health_service = HealthService(SqliteHealthProbe(database))
    auth_service = AuthService(
        SqliteEmployeeRepository(database),
        SqliteSessionRepository(database),
        clock or SystemClock(),
    )
    require_session = session_dependency(lambda: auth_service)

    # No public API docs: only login and health are served without a session (docs/security.md).
    app = FastAPI(title="İzin Yöneticisi", docs_url=None, redoc_url=None, openapi_url=None)
    install_error_handling(app)
    app.include_router(health_router(lambda: health_service))
    app.include_router(auth_router(lambda: auth_service, require_session, cookie_secure))
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


def app_from_env() -> FastAPI:
    """Server entry point: settings from the environment (.env.example)."""
    db_path = Path(os.environ.get("LEAVE_DB_PATH", "data/leave.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_app(str(db_path), cookie_secure=os.environ.get("LEAVE_COOKIE_SECURE") == "1")
