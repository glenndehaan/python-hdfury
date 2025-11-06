"""HDFury Client Exceptions."""

class HDFuryError(Exception):
    """Base exception for HDFury client."""


class HDFuryConnectionError(HDFuryError):
    """HDFury connection exception."""


class HDFuryParseError(HDFuryError):
    """HDFury parse exception."""
