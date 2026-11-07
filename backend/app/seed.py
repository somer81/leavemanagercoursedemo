"""Composition root for the demo-users seed.

Run: DEMO_PASSWORD=... .venv/bin/python -m app.seed   (from backend/, or with PYTHONPATH=backend)
"""

import os
import sys
from collections.abc import Mapping
from pathlib import Path

from app.domain.errors import InvalidInput
from app.repositories.connection import Database
from app.repositories.employee_repository import SqliteEmployeeRepository
from app.services.demo_users import DEMO_USERS, create_demo_users


def main(env: Mapping[str, str]) -> int:
    db_path = Path(env.get("LEAVE_DB_PATH", "data/leave.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        create_demo_users(
            SqliteEmployeeRepository(Database(str(db_path))), env.get("DEMO_PASSWORD")
        )
    except InvalidInput:
        # Never print the password itself.
        print(
            "DEMO_PASSWORD eksik veya 5–128 karakter dışında; kullanıcı oluşturulmadı.",
            file=sys.stderr,
        )
        return 1
    print("Demo kullanıcıları hazır: " + ", ".join(user[0] for user in DEMO_USERS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.environ))
