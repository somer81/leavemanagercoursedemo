"""Domain errors. The API layer maps them to HTTP in one place (docs/conventions.md)."""


class DomainError(Exception):
    """Base class for every business-rule or availability error raised below the API."""


class DataStoreUnavailable(DomainError):
    """The data store cannot be reached. Carries no internal detail (path, SQL)."""
