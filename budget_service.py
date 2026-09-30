"""Monthly category budgets and threshold alerts."""
from typing import List

from . import config, validators
from .database import Database
from .exceptions import NotFoundError
from .logger_setup import get_logger
from .models import Budget, BudgetStatus

log = get_logger("budgets")


def classify(percent: float) -> str:
    """Map percentage of budget used to an alert level."""
    if percent >= 100:
        return "EXCEEDED"
    if percent >= config.WARNING_THRESHOLD:
        return "WARNING"
    return "OK"


class BudgetService:
    def __init__(self, db: Database):
        self.db = db

    def set_budget(self, user_id: int, category: str, limit) -> Budget:
        category = validators.validate_category(category)
        limit = validators.validate_amount(limit)
        with self.db.session() as conn:
            conn.execute(
                "INSERT INTO budgets (user_id, category, monthly_limit) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit",
                (user_id, category, limit))
            row = conn.execute("SELECT * FROM budgets WHERE user_id = ? AND category = ?",
                               (user_id, category)).fetchone()
        log.info("User %s set budget %s = %.2f", user_id, category, limit)
        return Budget(row["id"], row["user_id"], row["category"], row["monthly_limit"])

    def remove_budget(self, user_id: int, category: str) -> None:
        category = validators.validate_category(category)
        with self.db.session() as conn:
            cur = conn.execute("DELETE FROM budgets WHERE user_id = ? AND category = ?",
                               (user_id, category))
            if cur.rowcount == 0:
                raise NotFoundError(f"No budget set for {category}.")

    def status(self, user_id: int, month: str) -> List[BudgetStatus]:
        """Spent vs limit for every budgeted category in the given month."""
        month = validators.validate_month(month)
        with self.db.session() as conn:
            budgets = conn.execute("SELECT category, monthly_limit FROM budgets "
                                   "WHERE user_id = ? ORDER BY category", (user_id,)).fetchall()
            spent_rows = conn.execute(
                "SELECT category, SUM(amount) AS total FROM expenses "
                "WHERE user_id = ? AND substr(date, 1, 7) = ? GROUP BY category",
                (user_id, month)).fetchall()
        spent = {r["category"]: r["total"] for r in spent_rows}
        result = []
        for b in budgets:
            used = round(spent.get(b["category"], 0.0), 2)
            pct = round(used / b["monthly_limit"] * 100, 1)
            result.append(BudgetStatus(b["category"], b["monthly_limit"], used, pct, classify(pct)))
        return result

    def alerts(self, user_id: int, month: str) -> List[BudgetStatus]:
        return [s for s in self.status(user_id, month) if s.level != "OK"]
