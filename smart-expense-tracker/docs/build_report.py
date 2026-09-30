"""Builds the project report PDF.  Edit the STUDENT_* values below, then run:
        python docs/build_report.py
Requires: reportlab (pip install reportlab)."""
import glob
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle, KeepTogether)

# ------------------------- EDIT THESE ---------------------------------
STUDENT_NAME = "Yash Tripathi"
STUDENT_REG_NO = "26BCE10516"
COURSE = "Python Programming"
SUBMISSION_DATE = "30 September 2026"
GITHUB_URL = "https://github.com/yash26bce10516/smart-expense-tracker"
# ----------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAG = os.path.join(ROOT, "docs", "diagrams")
SHOTS = os.path.join(ROOT, "docs", "screens")
OUT = os.path.join(ROOT, "docs", "Project_Report.pdf")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("Body", parent=ss["BodyText"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=17, spaceBefore=6, spaceAfter=10, textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#2C5282"))
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=9, leading=12, alignment=0, spaceAfter=0)
CELLB = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
CAP = ParagraphStyle("Cap", parent=BODY, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
CODE = ParagraphStyle("Code", parent=ss["Code"], fontSize=8, leading=10, backColor=colors.HexColor("#F4F4F4"),
                      borderPadding=6, spaceAfter=8)
BUL = ParagraphStyle("Bul", parent=BODY, leftIndent=14, bulletIndent=2, spaceAfter=3, alignment=0)


def P(t, s=BODY): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BUL, bulletText="\u2022") for i in items]


def table(rows, widths, header=True):
    data = [[Paragraph(str(c), CELLB if (header and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B7C3")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C5282"))]
        st += [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5FA")])]
    t.setStyle(TableStyle(st))
    return t


def figure(path, caption, max_w=16.5 * cm, max_h=19 * cm):
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(path).getSize()
    scale = min(max_w / w, max_h / h)
    return KeepTogether([Image(path, width=w * scale, height=h * scale), Spacer(1, 3), P(caption, CAP), Spacer(1, 8)])


def loc(path):
    with open(path, encoding="utf-8") as fh:
        return sum(1 for ln in fh if ln.strip())


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8.5); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, 1.2 * cm, "Smart Expense Tracker & Budget Analyzer - Project Report")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    s = []
    # ---------------- 1. Cover page ----------------
    s += [Spacer(1, 3.5 * cm), P("VITyarthi - Build Your Own Project", ParagraphStyle("c0", parent=BODY, alignment=TA_CENTER, fontSize=13, textColor=colors.HexColor("#E8590C"))),
          Spacer(1, 1 * cm),
          P("<b>Smart Expense Tracker &amp; Budget Analyzer</b>", ParagraphStyle("c1", parent=H1, fontSize=28, leading=34, alignment=TA_CENTER)),
          Spacer(1, 0.4 * cm),
          P("A multi-user, menu-driven Python application with budget alerts and spending analytics", ParagraphStyle("c2", parent=BODY, alignment=TA_CENTER, fontSize=13)),
          Spacer(1, 3 * cm)]
    cover = [["Student Name", STUDENT_NAME], ["Registration No.", STUDENT_REG_NO], ["Course", COURSE],
             ["Submission Date", SUBMISSION_DATE], ["GitHub Repository", GITHUB_URL]]
    s.append(table(cover, [5 * cm, 11 * cm], header=False))
    s.append(PageBreak())

    # ---------------- Contents ----------------
    s.append(P("Table of Contents", H1))
    toc = ["1. Cover Page", "2. Introduction", "3. Problem Statement", "4. Functional Requirements", "5. Non-Functional Requirements",
           "6. System Architecture", "7. Design Diagrams", "8. Design Decisions &amp; Rationale", "9. Implementation Details",
           "10. Screenshots / Results", "11. Testing Approach", "12. Challenges Faced", "13. Learnings &amp; Key Takeaways",
           "14. Future Enhancements", "15. References"]
    s += [P(t) for t in toc] + [PageBreak()]

    # ---------------- 2. Introduction ----------------
    s.append(P("2. Introduction", H1))
    s.append(P("Managing personal money is one of the first real-world problems a student faces. Most people track spending "
               "loosely - in memory, in a notes app or in a spreadsheet - and only realise they have overspent after the "
               "month is over. <b>Smart Expense Tracker &amp; Budget Analyzer</b> is a Python application that makes tracking "
               "effortless and, more importantly, gives <i>early warnings</i> while there is still time to change behaviour."))
    s.append(P("The project applies the core concepts of the Python course: functions, classes and dataclasses, modules and "
               "packages, file handling (CSV), exception handling, the standard library (<font face='Courier'>sqlite3, hashlib, hmac, "
               "logging, csv, calendar, unittest</font>), and clean layered design. It is a menu-driven command-line program "
               "with SQLite storage, so it runs anywhere Python 3.9+ is installed with <b>no third-party dependencies</b>."))
    s.append(P("Key capabilities: secure multi-user accounts; expense CRUD with filtering; per-category monthly budgets with "
               "WARNING (80%) and EXCEEDED (100%) alerts; monthly reports with ASCII charts; a trend view and a linear month-end "
               "forecast; and CSV import/export."))

    # ---------------- 3. Problem statement ----------------
    s.append(P("3. Problem Statement", H1))
    s.append(P("Students and young professionals often lose track of where their money goes. Spreadsheets are tedious to "
               "maintain; many mobile apps are cloud-based (privacy concerns), ad-supported or too complex; and very few warn "
               "the user <i>before</i> a category budget is exceeded. The result is that overspending is discovered too late."))
    s.append(P("<b>Objectives</b>"))
    s += bullets(["Provide a fast, private, offline way to record and manage expenses.",
                  "Let each user define monthly budgets per category and alert them at 80% and 100% usage.",
                  "Give clear analytics (monthly summary, category breakdown, trend, forecast) to support better decisions.",
                  "Protect user data with hashed passwords, strict per-user data isolation and validated input.",
                  "Deliver a well-structured, tested, documented and maintainable Python code base."])
    s.append(P("<b>Scope.</b> In scope: accounts, expense CRUD, budgets/alerts, analytics, CSV import/export, logging, tests. "
               "Out of scope: GUI/web/mobile front-ends, multi-currency, cloud sync and bank integration (see Future Enhancements). "
               "<b>Target users:</b> college students and young professionals who want a simple private expense log."))

    # ---------------- 4. Functional requirements ----------------
    s.append(P("4. Functional Requirements", H1))
    s.append(P("The system is organised into <b>five major functional modules</b> (the guidelines require at least three), each with a "
               "clear input/output contract."))
    fr = [["ID", "Module", "Requirement", "Input -> Output"],
          ["FR1", "User management", "Register a new account with a unique username and a password of at least 6 characters.", "username, password -> new user / error"],
          ["FR2", "User management", "Log in with username and password; unknown user and wrong password give the same message.", "credentials -> session user / error"],
          ["FR3", "Expense management", "Add an expense (amount, category, description, date).", "4 fields -> saved expense id"],
          ["FR4", "Expense management", "View expenses, filtered by month, category and/or description keyword; show total.", "filters -> table + total"],
          ["FR5", "Expense management", "Edit any field of an existing expense (Enter keeps current value).", "id + new values -> updated expense"],
          ["FR6", "Expense management", "Delete an expense after confirmation.", "id + y/N -> deleted"],
          ["FR7", "Budgets & alerts", "Set / update a monthly budget for a category (upsert).", "category, limit -> budget"],
          ["FR8", "Budgets & alerts", "Show spent vs limit per category for a month with level OK / WARNING (>=80%) / EXCEEDED (>=100%).", "month -> status table"],
          ["FR9", "Budgets & alerts", "Automatically warn right after adding an expense that pushes a category over a threshold.", "new expense -> alert message"],
          ["FR10", "Analytics", "Monthly report: count, total, largest, daily average, category ASCII bar chart, top-3 expenses.", "month -> report"],
          ["FR11", "Analytics", "Multi-month spending trend and linear month-end forecast.", "month -> trend + projection"],
          ["FR12", "Import / export", "Export all expenses to CSV; import from CSV, skipping and reporting invalid rows by line number.", "path -> counts + error list"]]
    s.append(table(fr, [1.2 * cm, 3 * cm, 7.6 * cm, 4.6 * cm]))
    s.append(Spacer(1, 6))
    s.append(P("<b>Workflow.</b> Start -> Login/Register -> Main menu -> choose a feature -> input is validated -> data is read/written in a "
               "database transaction -> result (and any alert) is displayed -> back to the main menu -> Logout. The full flowchart is in Section 7."))

    # ---------------- 5. Non-functional ----------------
    s.append(P("5. Non-Functional Requirements", H1))
    s.append(P("The guidelines require at least four; the project specifies and implements eight. Each is verifiable."))
    nfr = [["ID", "Category", "Requirement", "How it is met / verified"],
           ["NFR1", "Security", "Passwords never stored in plain text; users cannot access each other's data; no SQL injection.",
            "Salted PBKDF2-HMAC-SHA256 (600,000 iterations), constant-time comparison; every query filters by user_id; parameterised SQL. Tests: hashing, isolation, injection."],
           ["NFR2", "Performance", "Typical operations complete in well under one second with thousands of records.",
            "Index on (user_id, date); SQL aggregation. Measured with 10,000 rows: list month 7 ms, three analytics queries 15 ms, single add 5 ms."],
           ["NFR3", "Usability", "Clear menus, sensible defaults (today's date / current month), friendly error messages.",
            "Prompts show defaults; errors never show stack traces; the password prompt hides input."],
           ["NFR4", "Reliability", "A failed operation must never corrupt data or crash the session.",
            "Transactional Database.session() with rollback; DB CHECK constraints; last-resort exception guard in the CLI loop."],
           ["NFR5", "Maintainability", "Layered, modular code with single-responsibility modules.",
            "12 modules (presentation / business / data / cross-cutting); docstrings; constants in config.py."],
           ["NFR6", "Error-handling strategy", "Every failure maps to a specific, user-readable message.",
            "Custom hierarchy TrackerError -> ValidationError / AuthError / NotFoundError, caught in one dispatcher."],
           ["NFR7", "Logging / monitoring", "Important events and failures are recorded for diagnosis.",
            "Rotating log file (200 KB x 2 backups) with timestamp, level and module; failed logins logged as warnings."],
           ["NFR8", "Resource efficiency / portability", "Small footprint; runs anywhere without installation steps.",
            "Standard library only; single-file SQLite database; connections are opened per operation and always closed."]]
    s.append(table(nfr, [1.3 * cm, 2.6 * cm, 5.2 * cm, 7.3 * cm]))

    # ---------------- 6. System architecture ----------------
    s.append(PageBreak())
    s.append(P("6. System Architecture", H1))
    s.append(P("The application follows a <b>layered architecture</b> so each concern can be changed or tested independently:"))
    s += bullets(["<b>Presentation layer</b> - <font face='Courier'>cli.py</font> and <font face='Courier'>main.py</font>: menus, prompts and output only; no business rules.",
                  "<b>Business-logic layer</b> - <font face='Courier'>auth.py, expense_service.py, budget_service.py, analytics.py, exporter.py</font>: all rules and calculations.",
                  "<b>Data layer</b> - <font face='Courier'>database.py</font>: schema creation and transactional sessions over a SQLite file.",
                  "<b>Cross-cutting</b> - <font face='Courier'>validators.py, exceptions.py, logger_setup.py, config.py, models.py</font> used by all layers."])
    s.append(figure(os.path.join(DIAG, "architecture.png"), "Figure 1 - System architecture diagram", max_h=15 * cm))
    s.append(P("Dependencies point downwards only (CLI -> services -> database), and the CLI receives its input/output functions by injection, "
               "which is what allows the complete menu workflow to be tested automatically without a keyboard."))

    # ---------------- 7. Design diagrams ----------------
    s.append(PageBreak())
    s.append(P("7. Design Diagrams", H1))
    s.append(P("7.1 Use Case Diagram", H2))
    s.append(figure(os.path.join(DIAG, "usecase.png"), "Figure 2 - Use case diagram (single actor: User)", max_h=14 * cm))
    s.append(P("Adding an expense <i>includes</i> input validation and <i>extends</i> to a budget alert when the 80% threshold is crossed.", BODY))
    s.append(PageBreak())
    s.append(P("7.2 Workflow Diagram", H2))
    s.append(figure(os.path.join(DIAG, "workflow.png"), "Figure 3 - Process / workflow diagram", max_h=21 * cm))
    s.append(PageBreak())
    s.append(P("7.3 Sequence Diagram", H2))
    s.append(figure(os.path.join(DIAG, "sequence.png"), "Figure 4 - Sequence diagram: adding an expense with budget check"))
    s.append(P("7.4 Class Diagram", H2))
    s.append(figure(os.path.join(DIAG, "class.png"), "Figure 5 - Class diagram"))
    s.append(PageBreak())
    s.append(P("7.5 ER Diagram and Schema", H2))
    s.append(figure(os.path.join(DIAG, "er.png"), "Figure 6 - Entity-relationship diagram", max_h=9 * cm))
    schema = [["Table", "Columns", "Constraints"],
              ["users", "id, username, password_hash, salt, created_at", "PK id; username UNIQUE"],
              ["expenses", "id, user_id, amount, category, description, date, created_at", "PK id; FK user_id -> users ON DELETE CASCADE; CHECK amount > 0; index (user_id, date)"],
              ["budgets", "id, user_id, category, monthly_limit", "PK id; FK user_id; CHECK monthly_limit > 0; UNIQUE (user_id, category)"]]
    s.append(table(schema, [2.4 * cm, 7 * cm, 7 * cm]))

    # ---------------- 8. Design decisions ----------------
    s.append(PageBreak())
    s.append(P("8. Design Decisions &amp; Rationale", H1))
    dd = [["Decision", "Alternatives considered", "Rationale"],
          ["SQLite for storage", "CSV / JSON files; MySQL", "Zero setup, part of the standard library, ACID transactions, supports SQL aggregation for reports, and a single-file database is easy to back up."],
          ["Layered modules with service classes", "One large script", "Separates UI from rules and data; each service is unit-testable; meets the modular-code expectation."],
          ["PBKDF2 with per-user random salt (stdlib)", "Plain text; unsalted SHA-256; bcrypt (needs pip)", "Plain/unsalted hashes are unsafe; PBKDF2 is available without dependencies and is a recognised standard. Iterations are configurable."],
          ["Identical error for bad user / bad password", "Distinct messages", "Prevents attackers from discovering which usernames exist (user enumeration)."],
          ["All queries scoped by user_id", "Trusting the UI to pass the right id", "Enforces isolation at the data layer; a user cannot read, edit or delete another user's expense (tested)."],
          ["Dates stored as ISO text (YYYY-MM-DD)", "Unix timestamps", "Sorts correctly as text, human-readable, and month filtering is a simple substr(date,1,7)."],
          ["Amounts rounded to 2 decimals, limited to 10,000,000", "Decimal type", "Adequate for a personal tracker and simple; the limit blocks absurd or accidental values. (Decimal is listed as a future improvement.)"],
          ["Dependency-injected input/output in the CLI", "Direct input()/print()", "Lets the entire menu workflow be tested end-to-end with scripted input."],
          ["Custom exception hierarchy", "Generic Exception / return codes", "One dispatcher converts expected errors to friendly messages while unexpected ones are logged."],
          ["Linear forecast (spent / days elapsed x days in month)", "Regression / ML", "Transparent, explainable and correct for the data available; past months return the real total and future months return 0."]]
    s.append(table(dd, [4 * cm, 3.8 * cm, 8.8 * cm]))

    # ---------------- 9. Implementation ----------------
    s.append(P("9. Implementation Details", H1))
    s.append(P("The code base is a Python package of 12 modules plus an entry point and 7 test files. Line counts (non-blank) are measured from the repository:"))
    mods = [("cli.py", "Menu-driven interface; input/output injected"), ("auth.py", "Register / login, PBKDF2 hashing"),
            ("expense_service.py", "Expense CRUD and filtered listing"), ("budget_service.py", "Budgets, status, alert levels"),
            ("analytics.py", "Summary, breakdown, trend, forecast, ASCII chart"), ("exporter.py", "CSV export / import with row-level errors"),
            ("database.py", "Schema + transactional session context manager"), ("validators.py", "Validation of every input type"),
            ("models.py", "Dataclasses: User, Expense, Budget, BudgetStatus"), ("exceptions.py", "Custom exception hierarchy"),
            ("logger_setup.py", "Rotating file logger"), ("config.py", "Constants and environment overrides")]
    rows = [["Module", "Responsibility", "Lines"]]
    total = 0
    for name, desc in mods:
        n = loc(os.path.join(ROOT, "expense_tracker", name)); total += n
        rows.append([name, desc, n])
    tests_loc = sum(loc(f) for f in glob.glob(os.path.join(ROOT, "tests", "*.py")))
    rows.append(["<b>Total (application)</b>", "", f"<b>{total}</b>"])
    rows.append(["tests/ (7 test files + fixtures)", "Unit and end-to-end tests", tests_loc])
    s.append(table(rows, [4 * cm, 10.2 * cm, 2.4 * cm]))
    s.append(Spacer(1, 8))
    s.append(P("Key implementation techniques", H2))
    s.append(P("<b>1. Transactional database sessions</b> - a context manager guarantees commit on success, rollback on error and closing of the connection:"))
    s.append(Preformatted('''@contextmanager
def session(self):
    conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn; conn.commit()
    except Exception:
        conn.rollback(); log.exception("Transaction rolled back"); raise
    finally:
        conn.close()''', CODE))
    s.append(P("<b>2. Secure password storage</b> - a random 16-byte salt per user and a constant-time comparison:"))
    s.append(Preformatted('''def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt,
                               config.PBKDF2_ITERATIONS).hex()
...
if not hmac.compare_digest(expected, actual):
    raise AuthError("Invalid username or password.")''', CODE))
    s.append(P("<b>3. Budget classification and forecast</b> - the alert level is a pure function (easy to test), and the forecast handles past, current and future months:"))
    s.append(Preformatted('''def classify(percent):
    if percent >= 100: return "EXCEEDED"
    if percent >= config.WARNING_THRESHOLD: return "WARNING"   # 80.0
    return "OK"

projected = round(spent / elapsed * days_in_month, 2) if elapsed else 0.0''', CODE))
    s.append(P("<b>4. Validation at the service boundary</b> - every service calls the validators before touching the database, so bad data cannot "
               "enter regardless of which front-end is used. <b>5. Safe updates</b> - <font face='Courier'>update()</font> whitelists column names "
               "through a dictionary of cleaner functions, so the dynamic SET clause can never contain user-supplied SQL."))
    s.append(P("<b>Version control.</b> The project was developed in Git with a series of small, descriptive commits (project skeleton, data layer, "
               "authentication, expense CRUD, budgets, analytics, CSV, CLI, tests, documentation)."))

    # ---------------- 10. Screenshots ----------------
    s.append(PageBreak())
    s.append(P("10. Screenshots / Results", H1))
    s.append(P("The screenshots below are the actual program output from a scripted demonstration session (user <i>student01</i>, September 2026 data)."))
    caps = {"01_add_and_alert.png": "Figure 7 - Adding expenses: WARNING at 90% of Entertainment budget",
            "02_view_expenses.png": "Figure 8 - Viewing expenses filtered by month",
            "03_budget_status.png": "Figure 9 - Budget status: Food is EXCEEDED (112.5%)",
            "04_monthly_report.png": "Figure 10 - Monthly report with category bar chart and top expenses"}
    for fn, cap in caps.items():
        p = os.path.join(SHOTS, fn)
        if os.path.exists(p):
            s.append(figure(p, cap, max_h=9 * cm))
    s.append(P("<b>Result summary.</b> For the demo data the report correctly computes 7 expenses totalling Rs. 15,500.00 (daily average Rs. 516.67); "
               "Food spend of Rs. 4,500 against a Rs. 4,000 budget is flagged EXCEEDED at 112.5%; Entertainment at 90% is flagged WARNING; and the "
               "trend view lists August (Rs. 1,400) before September (Rs. 15,500)."))

    # ---------------- 11. Testing ----------------
    s.append(P("11. Testing Approach", H1))
    s.append(P("Testing uses Python's built-in <font face='Courier'>unittest</font>. Each test gets a fresh temporary SQLite database, so tests are independent "
               "and never touch real data. Password hashing uses a low iteration count during tests only (via an environment variable) to keep the suite fast."))
    tests = [["Test file", "What is verified", "Tests"],
             ["test_validators.py", "Valid / invalid amounts, categories, dates, months, usernames, passwords, description length", "6"],
             ["test_auth.py", "Login success, identical errors for bad user/password, duplicate username, weak password, no plain-text password", "5"],
             ["test_expense_service.py", "CRUD, filters, partial update, delete, user isolation, SQL-injection text stored safely", "7"],
             ["test_budget_service.py", "Threshold boundaries (79.9 / 80 / 100), upsert, monthly scoping, alerts, remove", "5"],
             ["test_analytics.py", "Summary, empty month, breakdown, top-N, trend order, forecast (mid / past / future), ASCII chart", "9"],
             ["test_exporter.py", "CSV round-trip incl. commas, bad rows skipped with line numbers, missing file, bad header", "3"],
             ["test_cli.py", "End-to-end scripted sessions: full workflow and friendly error handling", "2"]]
    s.append(table(tests, [4.2 * cm, 11 * cm, 1.4 * cm]))
    s.append(Spacer(1, 6))
    s.append(P("<b>Result:</b> 37 tests, all passing (<font face='Courier'>python -m unittest discover -v</font>). <b>Validation / performance test:</b> with 10,000 "
               "expense rows, listing one month (1,073 rows) took 7 ms, three analytics queries took 15 ms and a single insert took 5 ms - comfortably meeting NFR2. "
               "<b>Manual testing:</b> the interactive program was exercised with invalid menu options, non-numeric ids, negative amounts, malformed dates and an unknown login."))

    # ---------------- 12. Challenges ----------------
    s.append(P("12. Challenges Faced", H1))
    s += bullets(["<b>Testing an interactive program.</b> Menus that call <font face='Courier'>input()</font> are hard to test. Solved by injecting the input, output and password functions into the App class so a full session can be scripted.",
                  "<b>Keeping users' data separate.</b> Forgetting a single <font face='Courier'>user_id</font> filter would leak data. Solved by making every service method take the user id and adding explicit isolation tests.",
                  "<b>Month-end forecasting edge cases.</b> A naive formula gives wrong answers for past and future months. Solved by treating a finished month as fully elapsed and a future month as zero, each covered by a test.",
                  "<b>A bug found by the demo run.</b> The trend chart initially sorted months by amount instead of chronologically. It was found while reviewing real output, fixed by adding a <font face='Courier'>sort_by_value</font> option, and locked in with a regression test.",
                  "<b>Password-hash strength vs. test speed.</b> Strong hashing (600,000 iterations, about 0.6 s) makes tests slow. Solved with a configurable iteration count that tests lower via an environment variable.",
                  "<b>Money and floating point.</b> Floats can produce values like 0.1+0.2. Amounts are rounded to two decimals at the validation boundary; using Decimal is noted as a future improvement."])

    # ---------------- 13. Learnings ----------------
    s.append(P("13. Learnings &amp; Key Takeaways", H1))
    s += bullets(["Separating presentation, business logic and data makes code easier to test, change and explain.",
                  "Validating at the service boundary is more robust than trusting the user interface.",
                  "Parameterised SQL, salted hashing and least-privilege data access are practical, low-cost security habits.",
                  "Context managers, dataclasses, custom exceptions and logging make Python code clearer and safer.",
                  "Writing tests early exposes design problems (such as untestable input()) and edge cases before users find them.",
                  "Reviewing real program output, not just passing tests, finds bugs that tests did not anticipate."])

    # ---------------- 14. Future ----------------
    s.append(P("14. Future Enhancements", H1))
    s += bullets(["A graphical (Tkinter) or web (Flask) front-end with real charts using Matplotlib.",
                  "Recurring expenses (rent, subscriptions) and reminders.",
                  "Use of the Decimal type or integer paise for exact currency arithmetic; multi-currency support.",
                  "Custom categories, tags and receipt attachments.",
                  "Machine-learning based category suggestion and anomaly detection for unusual spends.",
                  "Cloud backup / sync and bank or UPI statement import; account lockout after repeated failed logins."])

    # ---------------- 15. References ----------------
    s.append(P("15. References", H1))
    refs = ["Python Software Foundation. <i>Python 3 Documentation - sqlite3, hashlib, hmac, logging, csv, unittest, dataclasses.</i> https://docs.python.org/3/",
            "OWASP. <i>Password Storage Cheat Sheet.</i> https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
            "NIST. <i>SP 800-132: Recommendation for Password-Based Key Derivation (PBKDF2).</i> https://csrc.nist.gov/publications/detail/sp/800-132/final",
            "SQLite Consortium. <i>SQLite Documentation.</i> https://www.sqlite.org/docs.html",
            "Graphviz. <i>DOT Language documentation</i> (used to generate the diagrams). https://graphviz.org/doc/info/lang.html",
            "VITyarthi. <i>Build Your Own Project - General Project Instructions &amp; Submission Guidelines.</i>"]
    s += [P(f"[{i}] {r}", BODY) for i, r in enumerate(refs, 1)]

    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title="Smart Expense Tracker - Project Report", author=STUDENT_NAME)
    doc.build(s, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print("Report written to", OUT)


if __name__ == "__main__":
    build()
