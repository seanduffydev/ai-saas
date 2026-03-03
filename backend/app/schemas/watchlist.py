"""Pydantic schemas for watchlist API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class WatchlistItemCreate(BaseModel):
    """Request body for adding an item to the watchlist.

    Attributes:
        commodity_id: Commodity identifier (e.g. 'gold', 'silver').
    """

    commodity_id: str = Field(
        ..., description="Commodity identifier (e.g., 'gold', 'silver')"
    )


class WatchlistItem(BaseModel):
    """Single watchlist entry with metadata.

    Attributes:
        id: Record UUID.
        user_id: Owner user ID.
        commodity_id: Commodity identifier.
        order_index: Display order (lower first).
        added_at: Creation timestamp string.
    """

    id: str
    user_id: str
    commodity_id: str
    order_index: int
    added_at: str


class WatchlistInitializeResponse(BaseModel):
    """Response after initializing or reading default watchlist.

    Attributes:
        message: Status message.
        data: List of watchlist items (default or existing).
    """

    message: str
    data: list[WatchlistItem] = []


class WatchlistAddResponse(BaseModel):
    """Response for adding an item to watchlist (message + created row data)."""

    message: str
    data: list[Any] = []
