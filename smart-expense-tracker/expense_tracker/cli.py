"""Menu-driven command-line interface (presentation layer only - no business logic)."""
import getpass
from datetime import date

from . import config
from .analytics import Analytics, text_bar_chart
from .auth import AuthService
from .budget_service import BudgetService
from .database import Database
from .exceptions import TrackerError
from .exporter import export_csv, import_csv
from .expense_service import ExpenseService
from .logger_setup import get_logger

log = get_logger("cli")

AUTH_MENU = "\n=== Smart Expense Tracker ===\n1. Login\n2. Register\n0. Exit"
MAIN_MENU = (
    "\n--- Main Menu ---\n"
    "1. Add expense        2. View / search expenses\n"
    "3. Edit expense       4. Delete expense\n"
    "5. Set budget         6. Budget status & alerts\n"
    "7. Monthly report     8. Trend & forecast\n"
    "9. Export CSV        10. Import CSV\n"
    "0. Logout"
)


class App:
    def __init__(self, db_path=None, input_fn=input, output_fn=print, password_fn=getpass.getpass):
        self.db = Database(db_path or config.DB_PATH)
        self.auth = AuthService(self.db)
        self.expenses = ExpenseService(self.db)
        self.budgets = BudgetService(self.db)
        self.analytics = Analytics(self.db)
        self.ask, self.say, self.ask_secret = input_fn, output_fn, password_fn
        self.user = None

    # ---- helpers -------------------------------------------------------
    def _money(self, value: float) -> str:
        return f"{config.CURRENCY} {value:,.2f}"

    def _month(self) -> str:
        default = date.today().strftime("%Y-%m")
        return self.ask(f"Month (YYYY-MM) [{default}]: ").strip() or default

    def _print_expenses(self, items):
        if not items:
            self.say("No expenses found.")
            return
        self.say(f"{'ID':>4}  {'Date':<10}  {'Category':<13} {'Amount':>12}  Description")
        for e in items:
            self.say(f"{e.id:>4}  {e.date:<10}  {e.category:<13} {e.amount:>12,.2f}  {e.description}")
        self.say(f"Total: {self._money(sum(e.amount for e in items))} ({len(items)} items)")

    # ---- auth ----------------------------------------------------------
    def _login(self):
        self.user = self.auth.login(self.ask("Username: "), self.ask_secret("Password: "))
        self.say(f"Welcome back, {self.user.username}!")

    def _register(self):
        username = self.ask("Choose username: ")
        self.user = self.auth.register(username, self.ask_secret("Choose password: "))
        self.say(f"Account created. Welcome, {self.user.username}!")

    # ---- feature handlers ---------------------------------------------
    def _add(self):
        self.say("Categories: " + ", ".join(config.CATEGORIES))
        today = date.today().isoformat()
        e = self.expenses.add(
            self.user.id, self.ask("Amount: "), self.ask("Category: "),
            self.ask("Description: "), self.ask(f"Date [{today}]: ").strip() or today)
        self.say(f"Saved expense #{e.id}.")
        for a in self.budgets.alerts(self.user.id, e.date[:7]):
            if a.category == e.category:
                self.say(f"!! Budget {a.level}: {a.category} is at {a.percent}% "
                         f"({self._money(a.spent)} of {self._money(a.limit)})")

    def _view(self):
        month = self.ask("Filter month YYYY-MM (blank = all): ").strip() or None
        cat = self.ask("Filter category (blank = all): ").strip() or None
        kw = self.ask("Search description (blank = none): ").strip() or None
        self._print_expenses(self.expenses.list(self.user.id, month, cat, kw))

    def _edit(self):
        eid = int(self.ask("Expense ID to edit: "))
        cur = self.expenses.get(self.user.id, eid)
        self.say("Press Enter to keep the current value.")
        new = self.expenses.update(
            self.user.id, eid,
            amount=self.ask(f"Amount [{cur.amount}]: ").strip() or None,
            category=self.ask(f"Category [{cur.category}]: ").strip() or None,
            description=self.ask(f"Description [{cur.description}]: ").strip() or None,
            date=self.ask(f"Date [{cur.date}]: ").strip() or None)
        self.say(f"Updated expense #{new.id}.")

    def _delete(self):
        eid = int(self.ask("Expense ID to delete: "))
        if self.ask(f"Really delete #{eid}? (y/N): ").strip().lower() == "y":
            self.expenses.delete(self.user.id, eid)
            self.say("Deleted.")
        else:
            self.say("Cancelled.")

    def _set_budget(self):
        b = self.budgets.set_budget(self.user.id, self.ask("Category: "), self.ask("Monthly limit: "))
        self.say(f"Budget for {b.category} set to {self._money(b.monthly_limit)}.")

    def _budget_status(self):
        month = self._month()
        rows = self.budgets.status(self.user.id, month)
        if not rows:
            self.say("No budgets set yet (use option 5).")
        for s in rows:
            self.say(f"{s.category:<13} {self._money(s.spent):>16} / {self._money(s.limit):<16} "
                     f"{s.percent:>6}%  [{s.level}]")

    def _report(self):
        month = self._month()
        s = self.analytics.monthly_summary(self.user.id, month)
        self.say(f"\nReport for {s['month']}: {s['count']} expenses, total {self._money(s['total'])}, "
                 f"largest {self._money(s['largest'])}, daily avg {self._money(s['daily_average'])}")
        for line in text_bar_chart(self.analytics.category_breakdown(self.user.id, month)):
            self.say("  " + line)
        top = self.analytics.top_expenses(self.user.id, month)
        if top:
            self.say("Top expenses:")
            for d, amt, cat, desc in top:
                self.say(f"  {d}  {self._money(amt):>16}  {cat} {desc}")

    def _trend(self):
        trend = self.analytics.monthly_trend(self.user.id)
        self.say("Monthly spending trend:")
        for line in text_bar_chart(dict(trend), sort_by_value=False) or ["  (no data)"]:
            self.say("  " + line)
        f = self.analytics.forecast_month_end(self.user.id, self._month())
        self.say(f"Forecast: spent {self._money(f['spent_so_far'])} in {f['days_elapsed']} of "
                 f"{f['days_in_month']} days -> projected {self._money(f['projected_total'])}")

    def _export(self):
        path = self.ask("Output file [expenses_export.csv]: ").strip() or "expenses_export.csv"
        self.say(f"Exported {export_csv(self.expenses.list(self.user.id), path)} expenses to {path}.")

    def _import(self):
        imported, errors = import_csv(self.ask("CSV file path: ").strip(), self.expenses, self.user.id)
        self.say(f"Imported {imported} expenses; {len(errors)} rows rejected.")
        for err in errors[:10]:
            self.say("  " + err)

    # ---- main loops ----------------------------------------------------
    def _dispatch(self, handlers, choice):
        action = handlers.get(choice)
        if action is None:
            self.say("Invalid option, please try again.")
            return
        try:
            action()
        except TrackerError as exc:
            self.say(f"Error: {exc}")
        except ValueError:
            self.say("Error: please enter a valid number.")
        except Exception:  # last-resort guard: never crash the session
            log.exception("Unexpected error")
            self.say("Something went wrong. Details were written to the log file.")

    def _session(self):
        handlers = {"1": self._add, "2": self._view, "3": self._edit, "4": self._delete,
                    "5": self._set_budget, "6": self._budget_status, "7": self._report,
                    "8": self._trend, "9": self._export, "10": self._import}
        while self.user:
            self.say(MAIN_MENU)
            choice = self.ask("Choose: ").strip()
            if choice == "0":
                self.say(f"Goodbye, {self.user.username}.")
                self.user = None
            else:
                self._dispatch(handlers, choice)

    def run(self):
        handlers = {"1": self._login, "2": self._register}
        while True:
            self.say(AUTH_MENU)
            choice = self.ask("Choose: ").strip()
            if choice == "0":
                self.say("Bye!")
                return
            self._dispatch(handlers, choice)
            if self.user:
                self._session()


def run():
    App().run()
