"""HealthService: system health from the data-store probe (spec 0001, AC-1, AC-2)."""

from app.domain.errors import DataStoreUnavailable
from app.domain.health import ComponentStatus, HealthReport
from app.services.health_service import HealthService


class ReachableProbe:
    def ping(self) -> None:
        return None


class UnreachableProbe:
    def ping(self) -> None:
        raise DataStoreUnavailable()


def test_check_returns_ok_when_probe_succeeds() -> None:
    report = HealthService(ReachableProbe()).check()

    assert report == HealthReport(status=ComponentStatus.OK, database=ComponentStatus.OK)


def test_check_returns_unavailable_when_probe_fails() -> None:
    report = HealthService(UnreachableProbe()).check()

    assert report == HealthReport(
        status=ComponentStatus.UNAVAILABLE, database=ComponentStatus.UNAVAILABLE
    )
