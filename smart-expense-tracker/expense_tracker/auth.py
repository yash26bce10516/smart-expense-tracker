"""User management: registration and login with salted PBKDF2 password hashing."""
import hashlib
import hmac
import os
import sqlite3

from . import config, validators
from .database import Database
from .exceptions import AuthError
from .logger_setup import get_logger
from .models import User

log = get_logger("auth")


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt,
                               config.PBKDF2_ITERATIONS).hex()


class AuthService:
    def __init__(self, db: Database):
        self.db = db

    def register(self, username: str, password: str) -> User:
        username = validators.validate_username(username)
        validators.validate_password(password)
        salt = os.urandom(16)
        try:
            with self.db.session() as conn:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, _hash_password(password, salt), salt.hex()),
                )
                user = User(cur.lastrowid, username)
        except sqlite3.IntegrityError:
            raise AuthError("That username is already taken.")
        log.info("Registered user '%s'", username)
        return user

    def login(self, username: str, password: str) -> User:
        username = (username or "").strip().lower()
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        # Same message for unknown user / wrong password: avoids user enumeration.
        if row is None:
            log.warning("Failed login for unknown user '%s'", username)
            raise AuthError("Invalid username or password.")
        expected = row["password_hash"]
        actual = _hash_password(password or "", bytes.fromhex(row["salt"]))
        if not hmac.compare_digest(expected, actual):
            log.warning("Failed login (bad password) for '%s'", username)
            raise AuthError("Invalid username or password.")
        log.info("User '%s' logged in", username)
        return User(row["id"], row["username"])
