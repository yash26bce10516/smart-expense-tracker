"""CSV export / import so data can be backed up or moved between systems."""
import csv
from typing import Iterable, List, Tuple

from .exceptions import TrackerError, ValidationError
from .expense_service import ExpenseService
from .logger_setup import get_logger
from .models import Expense

log = get_logger("exporter")
FIELDS = ["date", "amount", "category", "description"]


def export_csv(expenses: Iterable[Expense], path: str) -> int:
    count = 0
    try:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(FIELDS)
            for e in expenses:
                writer.writerow([e.date, f"{e.amount:.2f}", e.category, e.description])
                count += 1
    except OSError as exc:
        raise TrackerError(f"Could not write file: {exc}")
    log.info("Exported %d expenses to %s", count, path)
    return count


def import_csv(path: str, service: ExpenseService, user_id: int) -> Tuple[int, List[str]]:
    """Import rows; invalid rows are skipped and reported instead of aborting the run."""
    imported, errors = 0, []
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or not set(FIELDS) <= set(reader.fieldnames):
                raise TrackerError("CSV must have columns: " + ", ".join(FIELDS))
            for line_no, row in enumerate(reader, start=2):
                try:
                    service.add(user_id, row["amount"], row["category"],
                                row.get("description", ""), row["date"])
                    imported += 1
                except ValidationError as exc:
                    errors.append(f"Line {line_no}: {exc}")
    except FileNotFoundError:
        raise TrackerError(f"File not found: {path}")
    except OSError as exc:
        raise TrackerError(f"Could not read file: {exc}")
    log.info("Imported %d rows from %s (%d rejected)", imported, path, len(errors))
    return imported, errors
