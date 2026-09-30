# Project Statement

## Problem Statement
Students and young professionals often lose track of where their money goes. Spreadsheets are
tedious to maintain, most expense apps are cloud-based (privacy concerns) or cluttered with
ads, and few of them warn you *before* a category budget is blown. As a result, people
discover overspending only at the end of the month, when it is too late to react.

## Scope of the Project
**In scope**
- Multi-user accounts with secure (salted, hashed) passwords
- Recording, viewing, searching, editing and deleting expenses (CRUD)
- Monthly budgets per category with automatic WARNING / EXCEEDED alerts
- Monthly reports, category breakdown, spending trend and month-end forecast
- CSV export (backup) and CSV import (bulk load) with per-row error reporting
- Local storage in SQLite, logging, input validation and automated tests

**Out of scope (future work)**
- Graphical / web / mobile interface
- Multi-currency support and live exchange rates
- Cloud sync, bank/UPI integration, receipt scanning

## Target Users
- College students managing a monthly allowance
- Young professionals who want a simple, private, offline expense log
- Anyone who wants budget alerts without signing up for an online service

## High-Level Features
1. **User management** - register / login, salted PBKDF2 password hashing, per-user data isolation
2. **Expense management** - add, view (filter by month / category / keyword), edit, delete
3. **Budgeting** - set monthly limits per category; alerts at 80% (WARNING) and 100% (EXCEEDED)
4. **Analytics** - monthly summary, category bar chart, top expenses, trend, linear forecast
5. **Data portability** - CSV export and validated CSV import
6. **Reliability** - validation on every input, friendly errors, rotating log file, 37 unit/integration tests
