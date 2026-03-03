"""Common Pydantic schemas used across multiple API modules."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Standard success message response.

    Attributes:
        message: Human-readable success message.
    """

    message: str


class ErrorResponse(BaseModel):
    """Standard error response.

    Attributes:
        detail: Error message or detail string.
    """

    detail: str


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Status string (e.g. 'healthy').
    """

    status: str
