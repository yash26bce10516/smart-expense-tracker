import unittest

from expense_tracker.budget_service import classify
from expense_tracker.exceptions import NotFoundError, ValidationError
from tests.base import DBTestCase


class BudgetTests(DBTestCase):
    def test_classify_thresholds(self):
        self.assertEqual(classify(0), "OK")
        self.assertEqual(classify(79.9), "OK")
        self.assertEqual(classify(80), "WARNING")
        self.assertEqual(classify(99.9), "WARNING")
        self.assertEqual(classify(100), "EXCEEDED")

    def test_set_budget_upserts(self):
        self.budgets.set_budget(self.user.id, "Food", 1000)
        self.budgets.set_budget(self.user.id, "food", 2000)
        rows = self.budgets.status(self.user.id, "2026-09")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].limit, 2000)

    def test_status_and_alerts(self):
        self.budgets.set_budget(self.user.id, "Food", 1000)
        self.budgets.set_budget(self.user.id, "Transport", 500)
        self.expenses.add(self.user.id, 850, "Food", "", "2026-09-05")
        self.expenses.add(self.user.id, 100, "Transport", "", "2026-09-06")
        self.expenses.add(self.user.id, 900, "Food", "", "2026-08-06")   # other month
        status = {s.category: s for s in self.budgets.status(self.user.id, "2026-09")}
        self.assertEqual(status["Food"].percent, 85.0)
        self.assertEqual(status["Food"].level, "WARNING")
        self.assertEqual(status["Transport"].level, "OK")
        self.assertEqual([a.category for a in self.budgets.alerts(self.user.id, "2026-09")], ["Food"])

    def test_exceeded(self):
        self.budgets.set_budget(self.user.id, "Food", 100)
        self.expenses.add(self.user.id, 150, "Food", "", "2026-09-05")
        self.assertEqual(self.budgets.status(self.user.id, "2026-09")[0].level, "EXCEEDED")

    def test_invalid_and_remove(self):
        with self.assertRaises(ValidationError):
            self.budgets.set_budget(self.user.id, "Food", 0)
        with self.assertRaises(NotFoundError):
            self.budgets.remove_budget(self.user.id, "Food")
        self.budgets.set_budget(self.user.id, "Food", 10)
        self.budgets.remove_budget(self.user.id, "Food")


if __name__ == "__main__":
    unittest.main()
