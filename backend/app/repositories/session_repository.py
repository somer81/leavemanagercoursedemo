"""Sessions table (schema.sql): stored by token hash, created_at in UTC ISO 8601."""

from datetime import datetime

from app.domain.auth import StoredSession
from app.repositories.connection import Database


class SqliteSessionRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, session: StoredSession) -> None:
        with self._database.connect() as connection:
            connection.execute(
                "INSERT INTO sessions (token_hash, employee_id, created_at) VALUES (?, ?, ?)",
                (session.token_hash, session.employee_id, session.created_at.isoformat()),
            )

    def find(self, token_hash: str) -> StoredSession | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT token_hash, employee_id, created_at FROM sessions WHERE token_hash = ?",
                (token_hash,),
            ).fetchone()
        if row is None:
            return None
        return StoredSession(
            token_hash=str(row[0]),
            employee_id=int(row[1]),
            created_at=datetime.fromisoformat(str(row[2])),
        )

    def delete(self, token_hash: str) -> None:
        with self._database.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
