"""Portfolio management schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PortfolioPositionCreate(BaseModel):
    """Request body for creating a portfolio position"""
    commodity: str = Field(..., description="Commodity name")
    quantity: float = Field(..., gt=0, description="Quantity purchased (must be positive)")
    purchase_price: float = Field(..., gt=0, description="Price per unit at purchase")
    purchase_date: date = Field(..., description="Date of purchase (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class PortfolioPosition(BaseModel):
    """Portfolio position with calculated metrics"""
    id: str
    user_id: str
    commodity: str
    quantity: float
    purchase_price: float
    purchase_date: date
    notes: Optional[str]
    current_price: Optional[float]
    current_value: Optional[float]
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]


class DeletePositionResponse(BaseModel):
    """Response for position deletion"""
    message: str
    position_id: str
