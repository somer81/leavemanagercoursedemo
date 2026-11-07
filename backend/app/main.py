"""Composition root: wires the layers together.

Run: uvicorn --factory app.main:app_from_env --app-dir backend
"""

import os
from pathlib import Path

from fastapi import FastAPI

from app.api.health import health_router
from app.repositories.connection import connection_factory
from app.repositories.health_repository import SqliteHealthProbe
from app.services.health_service import HealthService


def create_app(db_path: str) -> FastAPI:
    health_service = HealthService(SqliteHealthProbe(connection_factory(db_path)))

    app = FastAPI(title="İzin Yöneticisi")
    app.include_router(health_router(lambda: health_service))
    return app


def app_from_env() -> FastAPI:
    """Server entry point: the database file from LEAVE_DB_PATH (.env.example)."""
    db_path = Path(os.environ.get("LEAVE_DB_PATH", "data/leave.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_app(str(db_path))
