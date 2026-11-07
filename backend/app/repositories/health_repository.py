"""Data-store probe: a trivial read proves the database answers."""

import sqlite3

from app.domain.errors import DataStoreUnavailable
from app.repositories.connection import ConnectionFactory


class SqliteHealthProbe:
    def __init__(self, connect: ConnectionFactory) -> None:
        self._connect = connect

    def ping(self) -> None:
        try:
            connection = self._connect()
            try:
                connection.execute("SELECT 1").fetchone()
            finally:
                connection.close()
        except sqlite3.Error as error:
            raise DataStoreUnavailable() from error
