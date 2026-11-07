"""Domain errors. The API layer maps them to HTTP in one place (docs/conventions.md)."""


class DomainError(Exception):
    """Base class for every business-rule or availability error raised below the API."""


class DataStoreUnavailable(DomainError):
    """The data store cannot be reached. Carries no internal detail (path, SQL)."""


class InvalidInput(DomainError):
    """A value breaks a format rule. Carries no echo of the value."""


class InvalidCredentials(DomainError):
    """Wrong password or unknown username — deliberately indistinguishable."""


class Unauthenticated(DomainError):
    """No session, or the session is unknown."""


class SessionExpired(DomainError):
    """The session is older than its lifetime."""
