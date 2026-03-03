"""Pydantic schemas for portfolio API requests and responses."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class PortfolioPositionCreate(BaseModel):
    """Request body for creating a portfolio position.

    Attributes:
        commodity: Commodity name.
        quantity: Quantity purchased (must be positive).
        purchase_price: Price per unit at purchase.
        purchase_date: Date of purchase (YYYY-MM-DD).
        notes: Optional notes (max 500 chars).
    """

    commodity: str = Field(..., description="Commodity name")
    quantity: float = Field(
        ..., gt=0, description="Quantity purchased (must be positive)"
    )
    purchase_price: float = Field(..., gt=0, description="Price per unit at purchase")
    purchase_date: date = Field(..., description="Date of purchase (YYYY-MM-DD)")
    notes: str | None = Field(None, max_length=500, description="Optional notes")


class PortfolioPosition(BaseModel):
    """Portfolio position with live and calculated metrics.

    Attributes:
        id: Position UUID.
        user_id: Owner user ID.
        commodity: Commodity name.
        quantity: Number of units.
        purchase_price: Price per unit at purchase.
        purchase_date: Purchase date.
        notes: Optional notes.
        current_price: Current market price (if available).
        current_value: quantity * current_price.
        profit_loss: current_value - (quantity * purchase_price).
        profit_loss_percent: Profit/loss as percentage of cost.
    """

    id: str
    user_id: str
    commodity: str
    quantity: float
    purchase_price: float
    purchase_date: date
    notes: str | None
    current_price: float | None
    current_value: float | None
    profit_loss: float | None
    profit_loss_percent: float | None


class PortfolioAddResponse(BaseModel):
    """Response after adding a portfolio position.

    Attributes:
        message: Success message.
        data: Created position row(s) from the database.
    """

    message: str
    data: list[Any] = []


class DeletePositionResponse(BaseModel):
    """Response after deleting a portfolio position.

    Attributes:
        message: Success message.
        position_id: Deleted position UUID.
    """

    message: str
    position_id: str
