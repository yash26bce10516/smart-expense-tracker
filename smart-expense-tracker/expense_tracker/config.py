"""Central configuration constants (single place to change behaviour)."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.environ.get("EXPENSE_DB", os.path.join(DATA_DIR, "expenses.db"))
LOG_PATH = os.environ.get("EXPENSE_LOG", os.path.join(DATA_DIR, "app.log"))

CATEGORIES = (
    "Food", "Transport", "Rent", "Utilities", "Shopping",
    "Health", "Education", "Entertainment", "Other",
)

MAX_AMOUNT = 10_000_000          # sanity limit for one expense
MIN_PASSWORD_LEN = 6
PBKDF2_ITERATIONS = int(os.environ.get("EXPENSE_PBKDF2_ITERS", 600_000))  # OWASP-recommended for SHA-256
WARNING_THRESHOLD = 80.0         # % of budget at which a warning is raised
CURRENCY = "Rs."
