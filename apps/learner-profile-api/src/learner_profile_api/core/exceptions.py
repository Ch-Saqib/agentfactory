"""Custom exceptions for the Learner Profile API."""


class ProfileNotFound(Exception):
    """Raised when a profile is not found for the given learner_id."""


class ConsentRequired(Exception):
    """Raised when profile creation is attempted without consent."""


class ConcurrencyConflict(Exception):
    """Raised when a concurrent update conflict is detected."""


class ProfileExists(Exception):
    """Raised when attempting to create a profile that already exists."""
