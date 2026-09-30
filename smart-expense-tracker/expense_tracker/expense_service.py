"""CRUD operations for expenses. All queries are scoped to the owning user."""
from typing import List, Optional

from . import validators
from .database import Database
from .exceptions import NotFoundError, ValidationError
from .logger_setup import get_logger
from .models import Expense

log = get_logger("expenses")


def _row_to_expense(row) -> Expense:
    return Expense(row["id"], row["user_id"], row["amount"], row["category"],
                   row["description"], row["date"])


class ExpenseService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, user_id: int, amount, category: str, description: str, date: str) -> Expense:
        amount = validators.validate_amount(amount)
        category = validators.validate_category(category)
        description = validators.validate_description(description)
        date = validators.validate_date(date)
        with self.db.session() as conn:
            cur = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, description, date) "
                "VALUES (?, ?, ?, ?, ?)", (user_id, amount, category, description, date))
            new_id = cur.lastrowid
        log.info("User %s added expense #%s (%.2f, %s)", user_id, new_id, amount, category)
        return Expense(new_id, user_id, amount, category, description, date)

    def get(self, user_id: int, expense_id: int) -> Expense:
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM expenses WHERE id = ? AND user_id = ?",
                               (expense_id, user_id)).fetchone()
        if row is None:
            raise NotFoundError(f"Expense #{expense_id} not found.")
        return _row_to_expense(row)

    def list(self, user_id: int, month: Optional[str] = None, category: Optional[str] = None,
             keyword: Optional[str] = None) -> List[Expense]:
        sql, params = "SELECT * FROM expenses WHERE user_id = ?", [user_id]
        if month:
            sql += " AND substr(date, 1, 7) = ?"
            params.append(validators.validate_month(month))
        if category:
            sql += " AND category = ?"
            params.append(validators.validate_category(category))
        if keyword:
            sql += " AND description LIKE ?"
            params.append(f"%{keyword.strip()}%")
        sql += " ORDER BY date DESC, id DESC"
        with self.db.session() as conn:
            return [_row_to_expense(r) for r in conn.execute(sql, params).fetchall()]

    def update(self, user_id: int, expense_id: int, **fields) -> Expense:
        current = self.get(user_id, expense_id)
        cleaners = {
            "amount": validators.validate_amount,
            "category": validators.validate_category,
            "description": validators.validate_description,
            "date": validators.validate_date,
        }
        updates = {}
        for key, value in fields.items():
            if key not in cleaners:
                raise ValidationError(f"Cannot update field '{key}'.")
            if value is not None:
                updates[key] = cleaners[key](value)
        if not updates:
            return current
        assignments = ", ".join(f"{k} = ?" for k in updates)
        with self.db.session() as conn:
            conn.execute(f"UPDATE expenses SET {assignments} WHERE id = ? AND user_id = ?",
                         (*updates.values(), expense_id, user_id))
        log.info("User %s updated expense #%s: %s", user_id, expense_id, list(updates))
        return self.get(user_id, expense_id)

    def delete(self, user_id: int, expense_id: int) -> None:
        with self.db.session() as conn:
            cur = conn.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?",
                               (expense_id, user_id))
            if cur.rowcount == 0:
                raise NotFoundError(f"Expense #{expense_id} not found.")
        log.info("User %s deleted expense #%s", user_id, expense_id)
