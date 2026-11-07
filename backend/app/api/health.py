"""GET /api/health — public by design (docs/security.md, spec 0001 R-3); status fields only."""

from collections.abc import Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.domain.health import ComponentStatus
from app.services.health_service import HealthService


def health_router(get_service: Callable[[], HealthService]) -> APIRouter:
    router = APIRouter()

    @router.get("/api/health")
    def read_health() -> JSONResponse:
        report = get_service().check()
        # A status report, not an error: 503 carries the same shape (docs/conventions.md).
        code = 200 if report.status is ComponentStatus.OK else 503
        return JSONResponse(
            status_code=code,
            content={"status": report.status.value, "database": report.database.value},
        )

    return router
