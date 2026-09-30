# Smart Expense Tracker & Budget Analyzer

A menu-driven, multi-user **command-line application written in Python** that records daily
expenses, enforces category budgets with early-warning alerts, and produces monthly analytics
(category breakdown, trend, month-end forecast). Data is stored locally in SQLite.

> Built for the *VITyarthi - Build Your Own Project* evaluation (Python course).

## Overview
Most people notice overspending only after the month ends. This tool lets you log expenses in
seconds, set a monthly limit for each category, and immediately warns you when you cross
**80 %** (WARNING) or **100 %** (EXCEEDED) of a budget. Reports and a simple forecast show where
the money goes and where the month is heading. See [`statement.md`](statement.md) for the full
problem statement, scope and target users.

## Features
| Module | What it does |
|---|---|
| **User management** | Register / login; passwords stored as salted PBKDF2-HMAC-SHA256 hashes; each user only sees their own data |
| **Expense management (CRUD)** | Add, list (filter by month / category / keyword), edit, delete expenses |
| **Budgets & alerts** | Monthly limit per category; instant WARNING (>= 80 %) / EXCEEDED (>= 100 %) alerts |
| **Analytics** | Monthly summary, ASCII category chart, top expenses, multi-month trend, month-end forecast |
| **Import / export** | CSV backup and bulk import; invalid rows are skipped and reported by line number |
| **Reliability** | Input validation, custom exceptions, transactional DB access, rotating log file |

## Technologies Used
- **Python 3.9+** (standard library only - no `pip install` needed)
- `sqlite3` (storage), `hashlib`/`hmac` (password security), `logging`, `csv`, `dataclasses`, `calendar`, `unittest`
- Git & GitHub for version control; Graphviz + Matplotlib only for generating the report diagrams

## Project Structure
```
smart-expense-tracker/
├── main.py                    # entry point
├── expense_tracker/
│   ├── cli.py                 # menu-driven interface (presentation layer)
│   ├── auth.py                # registration / login, password hashing
│   ├── expense_service.py     # expense CRUD
│   ├── budget_service.py      # budgets and alert levels
│   ├── analytics.py           # reports, trend, forecast, ASCII charts
│   ├── exporter.py            # CSV export / import
│   ├── database.py            # SQLite schema + transactional sessions
│   ├── validators.py          # input validation
│   ├── models.py              # dataclasses (User, Expense, Budget, BudgetStatus)
│   ├── exceptions.py          # custom exception hierarchy
│   ├── logger_setup.py        # rotating file logger
│   └── config.py              # constants / settings
├── tests/                     # 37 unit + end-to-end tests
├── docs/                      # diagrams (.dot + .png) and screenshots
├── data/                      # SQLite DB and log are created here at runtime
├── statement.md
└── README.md
```

## Installation & Running (step by step)

These steps assume you have never seen this project before. Everything runs in a terminal; no GUI is needed.

### 1. Prerequisites
- **Python 3.9 or newer.** Check with `python --version` (use `python3 --version` on Linux/macOS).
  Download from https://www.python.org/downloads/ if it is missing.
- **Git** (only needed to clone; you can also download the repository as a ZIP from GitHub).

### 2. Get the code
```bash
git clone https://github.com/yash26bce10516/smart-expense-tracker.git
cd smart-expense-tracker
```

### 3. Environment setup (optional but recommended)
A virtual environment keeps things clean. It is optional because the project has no dependencies.
```bash
python -m venv .venv
# Windows (PowerShell):   .venv\Scripts\Activate.ps1
# Windows (cmd):          .venv\Scripts\activate.bat
# Linux / macOS:          source .venv/bin/activate
```

### 4. Install dependencies
**There is nothing to install.** The application uses only the Python standard library
(`requirements.txt` documents this). Skip straight to step 6.

### 5. Configuration (optional)
The defaults work out of the box. The database (`data/expenses.db`) and log file (`data/app.log`)
are created automatically on first run. To change locations, set environment variables first:
```bash
# Linux / macOS
export EXPENSE_DB=/path/to/my.db
export EXPENSE_LOG=/path/to/app.log
# Windows PowerShell
$env:EXPENSE_DB="C:\\path\\my.db"
```
Other settings (categories, warning threshold, currency label) are constants in `expense_tracker/config.py`.

### 6. Run the application
```bash
python main.py            # use `python3 main.py` on Linux/macOS
```

### 7. First-use walkthrough (2 minutes)
1. Choose **2 (Register)** and create a username (3-20 letters/digits/underscore) and a password (6+ characters).
2. Choose **5** to set a budget, e.g. category `Food`, limit `4000`.
3. Choose **1** to add expenses, e.g. amount `1200`, category `Food`, a description, and a date (press Enter for today).
   When a category reaches 80% of its budget you will see a WARNING; at 100% it says EXCEEDED.
4. Choose **2** to view/search expenses, **7** for the monthly report, **8** for trend and forecast.
5. Choose **9** to export a CSV backup, **0** to log out.

Input format reminders: dates are `YYYY-MM-DD`, months are `YYYY-MM`. Valid categories:
Food, Transport, Rent, Utilities, Shopping, Health, Education, Entertainment, Other.

### Troubleshooting
| Problem | Fix |
|---|---|
| `python: command not found` | Use `python3`, or install Python and re-open the terminal |
| `ModuleNotFoundError: expense_tracker` | Run commands from the repository root (the folder containing `main.py`) |
| Want a clean start | Delete the `data/expenses.db` file |

## Testing
```bash
python -m unittest discover -v
```
Runs 37 tests covering validation, authentication (hashing, duplicate users, enumeration-safe
errors), expense CRUD and user isolation, SQL-injection safety, budget thresholds, analytics and
forecast maths, CSV round-trip / bad rows, and a scripted end-to-end run of the CLI.

## Screenshots
| Add expense + alerts | View expenses |
|---|---|
| ![add](docs/screens/01_add_and_alert.png) | ![view](docs/screens/02_view_expenses.png) |
| **Budget status** | **Monthly report** |
| ![budget](docs/screens/03_budget_status.png) | ![report](docs/screens/04_monthly_report.png) |

## Design Diagrams
Architecture, workflow, use-case, sequence, class and ER diagrams are in [`docs/diagrams/`](docs/diagrams).

## Non-Functional Requirements (summary)
Security (hashed passwords, parameterised SQL) - Reliability (transactions, rollback) - Usability
(friendly errors, defaults) - Performance (indexed queries, < 1 s operations) - Maintainability
(layered, modular code) - Logging (rotating log file).

## Author
Yash Tripathi - 26BCE10516 - VIT
