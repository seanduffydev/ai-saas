"""Common schemas used across multiple modules"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Standard success message response"""
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
