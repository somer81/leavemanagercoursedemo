"""Data-store probe: a trivial read proves the database answers.

Database.connect turns reachability errors (unopenable, locked, not a database, corrupt) into
DataStoreUnavailable, which the service reports as "unavailable".
"""

from app.repositories.connection import Database


class SqliteHealthProbe:
    def __init__(self, database: Database) -> None:
        self._database = database

    def ping(self) -> None:
        with self._database.connect() as connection:
            connection.execute("SELECT 1").fetchone()
