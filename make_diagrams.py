"""Generates the sequence diagram and terminal screenshots (run: python docs/make_diagrams.py)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def sequence(path):
    actors = ["User", "CLI (App)", "ExpenseService", "Validators", "Database", "BudgetService"]
    xs = [1, 3.4, 5.9, 8.2, 10.4, 12.7]
    msgs = [  # (from, to, text, dashed)
        (0, 1, "choose 1 (Add expense)", False),
        (0, 1, "amount, category, description, date", False),
        (1, 2, "add(user_id, amount, ...)", False),
        (2, 3, "validate_amount / category / date", False),
        (3, 2, "cleaned values (or ValidationError)", True),
        (2, 4, "INSERT INTO expenses (transaction)", False),
        (4, 2, "new id", True),
        (2, 1, "Expense", True),
        (1, 5, "alerts(user_id, month)", False),
        (5, 4, "SELECT budgets + SUM(amount)", False),
        (4, 5, "rows", True),
        (5, 1, "BudgetStatus list (OK / WARNING / EXCEEDED)", True),
        (1, 0, "'Saved expense #n' + budget alert", True),
    ]
    fig, ax = plt.subplots(figsize=(13, 8.2))
    top, step = 9.0, 0.6
    for a, x in zip(actors, xs):
        ax.add_patch(FancyBboxPatch((x - 0.85, top), 1.7, 0.6, boxstyle="round,pad=0.05",
                                    fc="#D6E6F7", ec="#4A78B0"))
        ax.text(x, top + 0.3, a, ha="center", va="center", fontsize=9.5, weight="bold")
        ax.plot([x, x], [top, top - step * (len(msgs) + 1)], color="#888", ls="--", lw=1)
    for i, (s, d, text, dashed) in enumerate(msgs):
        y = top - step * (i + 1)
        ax.annotate("", xy=(xs[d], y), xytext=(xs[s], y),
                    arrowprops=dict(arrowstyle="->", lw=1.3, color="#222", ls="--" if dashed else "-"))
        ax.text((xs[s] + xs[d]) / 2, y + 0.08, text, ha="center", va="bottom", fontsize=8.5)
    ax.set_xlim(-0.2, 14); ax.set_ylim(top - step * (len(msgs) + 1.6), top + 1)
    ax.axis("off"); ax.set_title("Sequence Diagram - Add Expense with Budget Check", fontsize=12, weight="bold")
    fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def terminal(text, path, title):
    lines = text.strip("\n").split("\n")
    h = 0.24 * len(lines) + 0.9
    fig = plt.figure(figsize=(10, h)); fig.patch.set_facecolor("#1e1e1e")
    fig.text(0.02, 1 - 0.35 / h, "* " + title, color="#9cdcfe", fontsize=9, family="monospace", va="center")
    for i, ln in enumerate(lines):
        color = "#f48771" if "EXCEEDED" in ln or "Error" in ln else "#e5c07b" if "WARNING" in ln else "#d4d4d4"
        fig.text(0.02, 1 - (0.75 + 0.24 * i) / h, ln, color=color, fontsize=9, family="monospace", va="center")
    fig.savefig(path, dpi=140, facecolor=fig.get_facecolor()); plt.close(fig)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    sequence(os.path.join(here, "diagrams", "sequence.png"))
    t = open("/tmp/demo/transcript.txt").read() if os.path.exists("/tmp/demo/transcript.txt") else ""
    def between(a, b):
        i = t.find(a); j = t.find(b, i)
        return t[i:j] if i >= 0 else ""
    shots = {
        "01_add_and_alert.png": ("Adding expenses - budget alerts", between("Choose: 1\nCategories: Food, Transport, Rent, Utilities, Shopping, Health, Education, Entertainment, Other\nAmount: 900", "\n--- Main Menu ---\n1. Add expense        2. View / search expenses\n3. Edit expense       4. Delete expense\n5. Set budget         6. Budget status & alerts\n7. Monthly report     8. Trend & forecast\n9. Export CSV        10. Import CSV\n0. Logout\nChoose: 1\nCategories: Food, Transport, Rent, Utilities, Shopping, Health, Education, Entertainment, Other\nAmount: 1800")),
        "02_view_expenses.png": ("View / filter expenses (month = 2026-09)", between("Filter month YYYY-MM", "\n--- Main Menu ---")),
        "03_budget_status.png": ("Budget status & alerts", between("Month (YYYY-MM) [2026-09]: 2026-09\nEntertainment", "\n--- Main Menu ---")),
        "04_monthly_report.png": ("Monthly report with category chart", between("Report for 2026-09", "\n--- Main Menu ---")),
    }
    os.makedirs(os.path.join(here, "screens"), exist_ok=True)
    for name, (title, txt) in shots.items():
        if txt.strip():
            terminal(txt, os.path.join(here, "screens", name), title)
    print("generated")
