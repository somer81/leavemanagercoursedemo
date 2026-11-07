"""Health of the system and its components."""

from dataclasses import dataclass
from enum import Enum


class ComponentStatus(Enum):
    OK = "ok"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class HealthReport:
    status: ComponentStatus
    database: ComponentStatus
