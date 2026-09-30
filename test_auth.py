import sqlite3
import unittest

from expense_tracker.exceptions import AuthError, ValidationError
from tests.base import DBTestCase


class AuthTests(DBTestCase):
    def test_login_success(self):
        user = self.auth.login("ALICE", "secret123")   # username is case-insensitive
        self.assertEqual(user.id, self.user.id)

    def test_wrong_password_and_unknown_user_same_message(self):
        with self.assertRaises(AuthError) as a:
            self.auth.login("alice", "wrongpass")
        with self.assertRaises(AuthError) as b:
            self.auth.login("nobody", "secret123")
        self.assertEqual(str(a.exception), str(b.exception))

    def test_duplicate_username_rejected(self):
        with self.assertRaises(AuthError):
            self.auth.register("Alice", "another123")

    def test_weak_password_rejected(self):
        with self.assertRaises(ValidationError):
            self.auth.register("bob", "123")

    def test_password_not_stored_in_plain_text(self):
        with self.db.session() as conn:
            row = conn.execute("SELECT password_hash, salt FROM users").fetchone()
        self.assertNotIn("secret123", row["password_hash"])
        self.assertEqual(len(row["password_hash"]), 64)   # sha256 hex digest
        self.assertTrue(row["salt"])


if __name__ == "__main__":
    unittest.main()
