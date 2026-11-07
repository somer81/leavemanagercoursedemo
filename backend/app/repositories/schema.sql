-- Applied idempotently on the first successful connection (repositories/connection.py).
CREATE TABLE IF NOT EXISTS employees (
    id            INTEGER PRIMARY KEY,
    username      TEXT    NOT NULL UNIQUE,          -- stored lower-case
    display_name  TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('EMPLOYEE', 'MANAGER', 'ADMIN')),
    manager_id    INTEGER REFERENCES employees (id),
    password_hash TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash  TEXT    PRIMARY KEY,                -- SHA-256 of the session token, never the token
    employee_id INTEGER NOT NULL REFERENCES employees (id),
    created_at  TEXT    NOT NULL                    -- UTC, ISO 8601
);
