"""Watchlist management schemas"""

from pydantic import BaseModel, Field
from typing import List


class WatchlistItemCreate(BaseModel):
    """Request body for adding item to watchlist"""
    commodity_id: str = Field(..., description="Commodity identifier (e.g., 'gold', 'silver')")


class WatchlistItem(BaseModel):
    """Watchlist item with metadata"""
    id: str
    user_id: str
    commodity_id: str
    order_index: int
    added_at: str


class WatchlistInitializeResponse(BaseModel):
    """Response for watchlist initialization"""
    message: str
    data: List[WatchlistItem] = []
