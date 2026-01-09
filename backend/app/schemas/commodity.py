"""Commodity-related schemas"""

from pydantic import BaseModel
from typing import List, Dict, Any


class CommodityInfo(BaseModel):
    """Commodity information response"""
    id: str
    name: str
    category: str
    symbol: str
    icon: str
    unit: str


class CommodityListResponse(BaseModel):
    """List of available commodities"""
    commodities: List[Dict[str, Any]]


class PriceData(BaseModel):
    """Individual price data point"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


class PriceHistoryResponse(BaseModel):
    """Historical price data response"""
    commodity: str
    commodity_info: Dict[str, Any]
    period: str
    data_points: int
    data: List[PriceData]
