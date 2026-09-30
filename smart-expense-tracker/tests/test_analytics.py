import unittest
from datetime import date

from expense_tracker.analytics import text_bar_chart
from tests.base import DBTestCase


class AnalyticsTests(DBTestCase):
    def setUp(self):
        super().setUp()
        add = lambda a, c, d, desc="": self.expenses.add(self.user.id, a, c, desc, d)
        add(300, "Food", "2026-09-01", "groceries")
        add(700, "Rent", "2026-09-02", "room")
        add(100, "Food", "2026-09-15", "snacks")
        add(50, "Transport", "2026-08-20")

    def test_monthly_summary(self):
        s = self.analytics.monthly_summary(self.user.id, "2026-09")
        self.assertEqual((s["count"], s["total"], s["largest"]), (3, 1100.0, 700.0))
        self.assertEqual(s["daily_average"], round(1100 / 30, 2))

    def test_empty_month(self):
        s = self.analytics.monthly_summary(self.user.id, "2020-01")
        self.assertEqual((s["count"], s["total"]), (0, 0))

    def test_category_breakdown(self):
        self.assertEqual(self.analytics.category_breakdown(self.user.id, "2026-09"),
                         {"Food": 400.0, "Rent": 700.0})

    def test_top_expenses_order(self):
        top = self.analytics.top_expenses(self.user.id, "2026-09", n=2)
        self.assertEqual([t[1] for t in top], [700.0, 300.0])

    def test_trend_oldest_first(self):
        self.assertEqual(list(self.analytics.monthly_trend(self.user.id)), ["2026-08", "2026-09"])

    def test_forecast_mid_month(self):
        f = self.analytics.forecast_month_end(self.user.id, "2026-09", today=date(2026, 9, 15))
        self.assertEqual(f["projected_total"], 2200.0)      # 1100 / 15 * 30

    def test_forecast_past_month_equals_actual(self):
        f = self.analytics.forecast_month_end(self.user.id, "2026-09", today=date(2026, 10, 5))
        self.assertEqual(f["projected_total"], 1100.0)

    def test_forecast_future_month_is_zero(self):
        f = self.analytics.forecast_month_end(self.user.id, "2027-01", today=date(2026, 9, 15))
        self.assertEqual(f["projected_total"], 0.0)

    def test_text_bar_chart(self):
        lines = text_bar_chart({"A": 10, "B": 5}, width=10)
        self.assertTrue(lines[0].startswith("A"))
        self.assertEqual(lines[0].count("#"), 10)
        self.assertEqual(lines[1].count("#"), 5)
        self.assertEqual(text_bar_chart({}), [])
        chrono = text_bar_chart({"2026-08": 1, "2026-09": 9}, sort_by_value=False)
        self.assertTrue(chrono[0].startswith("2026-08"))   # order preserved


if __name__ == "__main__":
    unittest.main()
