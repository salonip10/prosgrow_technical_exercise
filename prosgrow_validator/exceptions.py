"""Exceptions raised by the ProsGrow API client."""

from __future__ import annotations


class ProsGrowError(Exception):
    """Base class for all ProsGrow client errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class APIConnectionError(ProsGrowError):
    """The request never reached the ProsGrow API (network failure or timeout)."""


class AuthenticationError(ProsGrowError):
    """The API key was missing, invalid, or rejected (HTTP 401/403)."""


class RateLimitError(ProsGrowError):
    """The ProsGrow API reported the caller is being rate limited (HTTP 429)."""


class APIResponseError(ProsGrowError):
    """The API returned a non-success status, or a response with an unexpected shape."""
