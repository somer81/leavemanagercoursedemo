"""Data-store probe: a trivial read proves the database answers."""

import sqlite3

from app.domain.errors import DataStoreUnavailable
from app.repositories.connection import Database


class SqliteHealthProbe:
    def __init__(self, database: Database) -> None:
        self._database = database

    def ping(self) -> None:
        try:
            with self._database.connect() as connection:
                connection.execute("SELECT 1").fetchone()
        except sqlite3.Error as error:
            raise DataStoreUnavailable() from error
