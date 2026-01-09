"""Commodity-related endpoints"""

from fastapi import APIRouter, HTTPException
import pandas as pd

from app.data.fetchers.yahoo_fetcher import YahooFetcher
from app.schemas.commodity import CommodityListResponse, CommodityInfo, PriceHistoryResponse

router = APIRouter()


@router.get("/api/commodities", response_model=CommodityListResponse)
def get_commodities():
    """
    Get list of all available commodities.
    
    Returns a comprehensive list of commodities with their metadata including:
    - Name and display information
    - Category (metals, energy, agriculture)
    - Trading symbol
    - Icon for UI display
    - Unit of measurement
    """
    commodities = YahooFetcher.list_commodities()
    return {"commodities": commodities}


@router.get("/api/commodities/{commodity}", response_model=CommodityInfo)
def get_commodity_info(commodity: str):
    """
    Get detailed information about a specific commodity.
    
    Args:
        commodity: Commodity name (e.g., 'Gold', 'Silver', 'Crude Oil')
        
    Returns:
        Commodity information including symbol, category, icon, and unit
        
    Raises:
        HTTPException: 404 if commodity is not found
    """
    info = YahooFetcher.get_info(commodity)
    if not info:
        raise HTTPException(
            status_code=404, 
            detail=f"Commodity '{commodity}' not found"
        )
    
    symbol = YahooFetcher.get_symbol(commodity)
    return {"id": commodity, **info, "symbol": symbol}


@router.get("/api/prices/{commodity}", response_model=PriceHistoryResponse)
def get_prices(commodity: str, period: str = '1y'):
    """
    Fetch historical price data for a commodity.
    
    Args:
        commodity: Commodity name
        period: Time period (valid: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
    Returns:
        Historical OHLCV (Open, High, Low, Close, Volume) data
        
    Raises:
        HTTPException: 500 if data fetching fails
    """
    try:
        df = YahooFetcher.fetch_historical(commodity, period)
        
        data = []
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Handle date - might be datetime or string
            date_val = row['date']
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            data.append({
                'date': date_str,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']) if 'volume' in row and not pd.isna(row['volume']) else 0
            })
        
        info = YahooFetcher.get_info(commodity)
        return {
            "commodity": commodity,
            "commodity_info": info,
            "period": period,
            "data_points": len(data),
            "data": data
        }
    except Exception as e:
        print(f"Error in get_prices: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch price data: {str(e)}"
        )
