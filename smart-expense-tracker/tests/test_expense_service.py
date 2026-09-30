import unittest

from expense_tracker.exceptions import NotFoundError, ValidationError
from tests.base import DBTestCase


class ExpenseTests(DBTestCase):
    def add(self, amount=100, cat="Food", desc="lunch", day="2026-09-10"):
        return self.expenses.add(self.user.id, amount, cat, desc, day)

    def test_create_and_read(self):
        e = self.add(250.5, "food", "dinner")
        got = self.expenses.get(self.user.id, e.id)
        self.assertEqual((got.amount, got.category, got.description), (250.5, "Food", "dinner"))

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValidationError):
            self.add(amount=-10)
        with self.assertRaises(ValidationError):
            self.add(cat="Nope")
        with self.assertRaises(ValidationError):
            self.add(day="10/09/2026")

    def test_list_filters(self):
        self.add(100, "Food", "pizza", "2026-09-01")
        self.add(200, "Transport", "cab", "2026-09-02")
        self.add(300, "Food", "thali", "2026-10-01")
        self.assertEqual(len(self.expenses.list(self.user.id)), 3)
        self.assertEqual(len(self.expenses.list(self.user.id, month="2026-09")), 2)
        self.assertEqual(len(self.expenses.list(self.user.id, category="food")), 2)
        self.assertEqual(len(self.expenses.list(self.user.id, keyword="cab")), 1)

    def test_update(self):
        e = self.add()
        new = self.expenses.update(self.user.id, e.id, amount="150", description=None)
        self.assertEqual(new.amount, 150.0)
        self.assertEqual(new.description, "lunch")   # untouched
        with self.assertRaises(ValidationError):
            self.expenses.update(self.user.id, e.id, amount="-1")

    def test_delete(self):
        e = self.add()
        self.expenses.delete(self.user.id, e.id)
        with self.assertRaises(NotFoundError):
            self.expenses.get(self.user.id, e.id)
        with self.assertRaises(NotFoundError):
            self.expenses.delete(self.user.id, e.id)

    def test_users_are_isolated(self):
        bob = self.auth.register("bob", "bobpass1")
        e = self.add()
        with self.assertRaises(NotFoundError):
            self.expenses.get(bob.id, e.id)
        with self.assertRaises(NotFoundError):
            self.expenses.delete(bob.id, e.id)
        self.assertEqual(self.expenses.list(bob.id), [])

    def test_sql_injection_text_is_stored_safely(self):
        e = self.add(desc="x'); DROP TABLE expenses;--")
        self.assertEqual(len(self.expenses.list(self.user.id)), 1)
        self.assertIn("DROP TABLE", self.expenses.get(self.user.id, e.id).description)


if __name__ == "__main__":
    unittest.main()
