"""Logging configuration: rotating file log + quiet console output."""
import logging
import os
from logging.handlers import RotatingFileHandler

from . import config

_configured = False


def get_logger(name: str) -> logging.Logger:
    """Return a module logger; configure the root app logger once."""
    global _configured
    if not _configured:
        os.makedirs(os.path.dirname(config.LOG_PATH), exist_ok=True)
        root = logging.getLogger("expense_tracker")
        root.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
        fh = RotatingFileHandler(config.LOG_PATH, maxBytes=200_000, backupCount=2, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)
        root.propagate = False
        _configured = True
    return logging.getLogger(f"expense_tracker.{name}")
