"""Composition root: wires the layers together.

Run: uvicorn --factory app.main:app_from_env --app-dir backend
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.health import health_router
from app.repositories.connection import connection_factory
from app.repositories.health_repository import SqliteHealthProbe
from app.services.health_service import HealthService

# Only the public folder is served; frontend/tests stays private.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public"


def create_app(db_path: str) -> FastAPI:
    health_service = HealthService(SqliteHealthProbe(connection_factory(db_path)))

    # No public API docs: only login and health are served without a session (docs/security.md).
    app = FastAPI(title="İzin Yöneticisi", docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(health_router(lambda: health_service))
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


def app_from_env() -> FastAPI:
    """Server entry point: the database file from LEAVE_DB_PATH (.env.example)."""
    db_path = Path(os.environ.get("LEAVE_DB_PATH", "data/leave.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_app(str(db_path))
