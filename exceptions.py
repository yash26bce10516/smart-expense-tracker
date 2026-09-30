"""Custom exception hierarchy - lets the CLI show friendly messages."""


class TrackerError(Exception):
    """Base class for all application errors."""


class ValidationError(TrackerError):
    """Invalid user input."""


class AuthError(TrackerError):
    """Registration / login failure."""


class NotFoundError(TrackerError):
    """Requested record does not exist (or belongs to another user)."""
