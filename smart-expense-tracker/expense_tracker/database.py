"""SQLite access layer: schema creation and a transactional session helper."""
import os
import sqlite3
from contextlib import contextmanager

from .logger_setup import get_logger

log = get_logger("database")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      REAL NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    date        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS budgets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category      TEXT NOT NULL,
    monthly_limit REAL NOT NULL CHECK (monthly_limit > 0),
    UNIQUE (user_id, category)
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses (user_id, date);
"""


class Database:
    """Thin wrapper around sqlite3 that guarantees commit/rollback and closing."""

    def __init__(self, path: str):
        self.path = path
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with self.session() as conn:
            conn.executescript(SCHEMA)
        log.info("Database ready at %s", path)

    @contextmanager
    def session(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            log.exception("Transaction rolled back")
            raise
        finally:
            conn.close()
