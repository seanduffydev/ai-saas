import yfinance as yf
import pandas as pd
from typing import Optional

class YahooFetcher:
    """Fetch commodity price data from Yahoo Finance"""
    
    SYMBOLS = {
        'gold': 'GC=F',
        'silver': 'SI=F',
        'crude_oil': 'CL=F',
        'natural_gas': 'NG=F',
        'copper': 'HG=F',
        'wheat': 'ZW=F',
        'corn': 'ZC=F',
        'soybeans': 'ZS=F',
    }
    
    COMMODITY_INFO = {
        'gold': {'name': 'Gold', 'category': 'Metals', 'unit': 'USD/oz', 'icon': '🥇'},
        'silver': {'name': 'Silver', 'category': 'Metals', 'unit': 'USD/oz', 'icon': '🥈'},
        'crude_oil': {'name': 'Crude Oil (WTI)', 'category': 'Energy', 'unit': 'USD/barrel', 'icon': '🛢️'},
        'natural_gas': {'name': 'Natural Gas', 'category': 'Energy', 'unit': 'USD/MMBtu', 'icon': '⚡'},
        'copper': {'name': 'Copper', 'category': 'Metals', 'unit': 'USD/lb', 'icon': '🔶'},
        'wheat': {'name': 'Wheat', 'category': 'Agriculture', 'unit': 'USD/bushel', 'icon': '🌾'},
        'corn': {'name': 'Corn', 'category': 'Agriculture', 'unit': 'USD/bushel', 'icon': '🌽'},
        'soybeans': {'name': 'Soybeans', 'category': 'Agriculture', 'unit': 'USD/bushel', 'icon': '🫘'},
    }
    
    @staticmethod
    def get_symbol(commodity: str) -> Optional[str]:
        return YahooFetcher.SYMBOLS.get(commodity.lower())
    
    @staticmethod
    def get_info(commodity: str) -> Optional[dict]:
        return YahooFetcher.COMMODITY_INFO.get(commodity.lower())
    
    @staticmethod
    @staticmethod
    def fetch_historical(commodity: str, period: str = '5y') -> pd.DataFrame:
        symbol = YahooFetcher.get_symbol(commodity)
        if not symbol:
            raise ValueError(f"Unknown commodity: {commodity}")
        
        print(f"Fetching {commodity} data...")
        df = yf.download(symbol, period=period, progress=False)
        
        if df.empty:
            raise ValueError(f"No data available for {commodity}")
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Flatten multi-level columns (yfinance sometimes returns these)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if col[1] == '' else col[0] for col in df.columns]
        
        # Standardize column names to lowercase
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        print(f"Columns after flattening: {df.columns.tolist()}")
        
        # Keep only what we need
        columns_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume']
        existing_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[existing_columns]
        
        # Remove rows with missing values
        df = df.dropna()
        
        print(f"Fetched {len(df)} data points")
        return df
    
    @staticmethod
    def list_commodities():
        return [
            {
                'id': key,
                **YahooFetcher.COMMODITY_INFO[key],
                'symbol': YahooFetcher.SYMBOLS[key]
            }
            for key in YahooFetcher.SYMBOLS.keys()
        ]