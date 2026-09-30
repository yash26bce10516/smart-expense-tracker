"""Reporting & analytics: summaries, category breakdown, trends, month-end forecast."""
import calendar
from datetime import date
from typing import Dict, List, Optional, Tuple

from . import validators
from .database import Database


def text_bar_chart(data: Dict[str, float], width: int = 30, sort_by_value: bool = True) -> List[str]:
    """Render {label: value} as horizontal ASCII bars (largest first unless sort_by_value=False)."""
    if not data:
        return []
    peak = max(data.values()) or 1
    label_w = max(len(k) for k in data)
    lines = []
    items = sorted(data.items(), key=lambda kv: kv[1], reverse=True) if sort_by_value else list(data.items())
    for label, value in items:
        bar = "#" * max(1, int(round(value / peak * width))) if value > 0 else ""
        lines.append(f"{label:<{label_w}} | {bar} {value:,.2f}")
    return lines


class Analytics:
    def __init__(self, db: Database):
        self.db = db

    def monthly_summary(self, user_id: int, month: str) -> Dict:
        month = validators.validate_month(month)
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n, COALESCE(SUM(amount), 0) AS total, "
                "COALESCE(MAX(amount), 0) AS biggest FROM expenses "
                "WHERE user_id = ? AND substr(date, 1, 7) = ?", (user_id, month)).fetchone()
        year, mon = map(int, month.split("-"))
        days = calendar.monthrange(year, mon)[1]
        total = round(row["total"], 2)
        return {"month": month, "count": row["n"], "total": total,
                "largest": round(row["biggest"], 2), "daily_average": round(total / days, 2)}

    def category_breakdown(self, user_id: int, month: str) -> Dict[str, float]:
        month = validators.validate_month(month)
        with self.db.session() as conn:
            rows = conn.execute(
                "SELECT category, SUM(amount) AS total FROM expenses "
                "WHERE user_id = ? AND substr(date, 1, 7) = ? GROUP BY category", (user_id, month)
            ).fetchall()
        return {r["category"]: round(r["total"], 2) for r in rows}

    def top_expenses(self, user_id: int, month: str, n: int = 3) -> List[Tuple[str, float, str, str]]:
        month = validators.validate_month(month)
        with self.db.session() as conn:
            rows = conn.execute(
                "SELECT date, category, description, amount FROM expenses "
                "WHERE user_id = ? AND substr(date, 1, 7) = ? ORDER BY amount DESC LIMIT ?",
                (user_id, month, n)).fetchall()
        return [(r["date"], r["amount"], r["category"], r["description"]) for r in rows]

    def monthly_trend(self, user_id: int, months: int = 6) -> Dict[str, float]:
        """Total spend for the most recent N months that have data (oldest first)."""
        with self.db.session() as conn:
            rows = conn.execute(
                "SELECT substr(date, 1, 7) AS m, SUM(amount) AS total FROM expenses "
                "WHERE user_id = ? GROUP BY m ORDER BY m DESC LIMIT ?", (user_id, months)
            ).fetchall()
        return {r["m"]: round(r["total"], 2) for r in reversed(rows)}

    def forecast_month_end(self, user_id: int, month: str, today: Optional[date] = None) -> Dict:
        """Linear projection: (spent so far / days elapsed) * days in month.

        For a fully elapsed past month the projection equals the actual total.
        """
        month = validators.validate_month(month)
        today = today or date.today()
        year, mon = map(int, month.split("-"))
        days_in_month = calendar.monthrange(year, mon)[1]
        if (year, mon) < (today.year, today.month):
            elapsed = days_in_month
        elif (year, mon) > (today.year, today.month):
            elapsed = 0
        else:
            elapsed = today.day
        spent = self.monthly_summary(user_id, month)["total"]
        projected = round(spent / elapsed * days_in_month, 2) if elapsed else 0.0
        return {"month": month, "spent_so_far": spent, "days_elapsed": elapsed,
                "days_in_month": days_in_month, "projected_total": projected}
