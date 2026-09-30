"""Input validation helpers. Every function returns a cleaned value or raises ValidationError."""
import re
from datetime import datetime

from . import config
from .exceptions import ValidationError

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def validate_username(username: str) -> str:
    username = (username or "").strip()
    if not _USERNAME_RE.match(username):
        raise ValidationError("Username must be 3-20 characters: letters, digits or underscore.")
    return username.lower()


def validate_password(password: str) -> str:
    if password is None or len(password) < config.MIN_PASSWORD_LEN:
        raise ValidationError(f"Password must be at least {config.MIN_PASSWORD_LEN} characters.")
    return password


def validate_amount(value) -> float:
    try:
        amount = float(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError("Amount must be a number.")
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValidationError("Amount must be a finite number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if amount > config.MAX_AMOUNT:
        raise ValidationError(f"Amount cannot exceed {config.MAX_AMOUNT:,}.")
    return round(amount, 2)


def validate_category(category: str) -> str:
    cleaned = (category or "").strip().title()
    if cleaned not in config.CATEGORIES:
        raise ValidationError("Category must be one of: " + ", ".join(config.CATEGORIES))
    return cleaned


def validate_date(value: str) -> str:
    try:
        return datetime.strptime((value or "").strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format (e.g. 2026-09-30).")


def validate_month(value: str) -> str:
    try:
        return datetime.strptime((value or "").strip(), "%Y-%m").strftime("%Y-%m")
    except ValueError:
        raise ValidationError("Month must be in YYYY-MM format (e.g. 2026-09).")


def validate_description(text: str) -> str:
    text = (text or "").strip()
    if len(text) > 100:
        raise ValidationError("Description is limited to 100 characters.")
    return text
