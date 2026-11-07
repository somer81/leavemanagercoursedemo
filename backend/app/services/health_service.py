"""Reports system health from a data-store probe."""

from typing import Protocol

from app.domain.errors import DataStoreUnavailable
from app.domain.health import ComponentStatus, HealthReport


class HealthProbe(Protocol):
    def ping(self) -> None:
        """Return when the data store answers; raise DataStoreUnavailable otherwise."""


class HealthService:
    def __init__(self, probe: HealthProbe) -> None:
        self._probe = probe

    def check(self) -> HealthReport:
        try:
            self._probe.ping()
        except DataStoreUnavailable:
            return HealthReport(
                status=ComponentStatus.UNAVAILABLE, database=ComponentStatus.UNAVAILABLE
            )
        return HealthReport(status=ComponentStatus.OK, database=ComponentStatus.OK)
