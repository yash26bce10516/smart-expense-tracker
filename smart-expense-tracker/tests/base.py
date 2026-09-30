"""Shared fixture: every test gets a fresh temporary database and one registered user."""
import os
import tempfile
import unittest

from expense_tracker.auth import AuthService
from expense_tracker.budget_service import BudgetService
from expense_tracker.analytics import Analytics
from expense_tracker.database import Database
from expense_tracker.expense_service import ExpenseService


class DBTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self.tmp.name, "test.db"))
        self.auth = AuthService(self.db)
        self.expenses = ExpenseService(self.db)
        self.budgets = BudgetService(self.db)
        self.analytics = Analytics(self.db)
        self.user = self.auth.register("alice", "secret123")

    def tearDown(self):
        self.tmp.cleanup()
