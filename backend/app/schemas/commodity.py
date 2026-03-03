"""Pydantic schemas for commodity API requests and responses."""

from typing import Any, Dict, List

from pydantic import BaseModel


class CommodityInfo(BaseModel):
    """Commodity metadata for display.

    Attributes:
        id: Commodity identifier.
        name: Display name.
        category: Category (e.g. Metals, Energy).
        symbol: Yahoo Finance ticker.
        icon: Emoji or icon identifier.
        unit: Unit of measurement (e.g. USD/oz).
    """

    id: str
    name: str
    category: str
    symbol: str
    icon: str
    unit: str


class CommodityListResponse(BaseModel):
    """Response containing list of available commodities.

    Attributes:
        commodities: List of commodity dicts (id, name, category, etc.).
    """

    commodities: List[Dict[str, Any]]


class PriceData(BaseModel):
    """Single OHLCV price data point.

    Attributes:
        date: Date string.
        open: Open price.
        high: High price.
        low: Low price.
        close: Close price.
        volume: Volume (default 0).
    """

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int = 0


class PriceHistoryResponse(BaseModel):
    """Historical price series response.

    Attributes:
        commodity: Commodity name.
        commodity_info: Commodity metadata.
        period: Requested period (e.g. '1y').
        data_points: Number of points in data.
        data: List of PriceData points.
    """

    commodity: str
    commodity_info: Dict[str, Any]
    period: str
    data_points: int
    data: List[PriceData]
