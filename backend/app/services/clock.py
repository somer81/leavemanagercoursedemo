"""The service layer's only source of "now" (docs/conventions.md, Data rules)."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Current time, timezone-aware UTC."""
