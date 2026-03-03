"""Yahoo Finance data fetcher for commodity prices and metadata."""

import pandas as pd
import yfinance as yf


class YahooFetcher:
    """Fetches commodity price data and metadata from Yahoo Finance."""

    SYMBOLS = {
        "gold": "GC=F",
        "silver": "SI=F",
        "crude_oil": "CL=F",
        "natural_gas": "NG=F",
        "copper": "HG=F",
        "wheat": "ZW=F",
        "corn": "ZC=F",
        "soybeans": "ZS=F",
    }

    COMMODITY_INFO = {
        "gold": {"name": "Gold", "category": "Metals", "unit": "USD/oz", "icon": "🥇"},
        "silver": {
            "name": "Silver",
            "category": "Metals",
            "unit": "USD/oz",
            "icon": "🥈",
        },
        "crude_oil": {
            "name": "Crude Oil (WTI)",
            "category": "Energy",
            "unit": "USD/barrel",
            "icon": "🛢️",
        },
        "natural_gas": {
            "name": "Natural Gas",
            "category": "Energy",
            "unit": "USD/MMBtu",
            "icon": "⚡",
        },
        "copper": {
            "name": "Copper",
            "category": "Metals",
            "unit": "USD/lb",
            "icon": "🔶",
        },
        "wheat": {
            "name": "Wheat",
            "category": "Agriculture",
            "unit": "USD/bushel",
            "icon": "🌾",
        },
        "corn": {
            "name": "Corn",
            "category": "Agriculture",
            "unit": "USD/bushel",
            "icon": "🌽",
        },
        "soybeans": {
            "name": "Soybeans",
            "category": "Agriculture",
            "unit": "USD/bushel",
            "icon": "🫘",
        },
    }

    @staticmethod
    def get_symbol(commodity: str) -> str | None:
        """Map commodity name to Yahoo Finance ticker.

        Args:
            commodity: Commodity name (e.g. 'gold', 'Gold').

        Returns:
            Ticker symbol (e.g. 'GC=F') or None if unknown.
        """
        return YahooFetcher.SYMBOLS.get(commodity.lower())

    @staticmethod
    def get_info(commodity: str) -> dict | None:
        """Get display metadata for a commodity.

        Args:
            commodity: Commodity name (case-insensitive).

        Returns:
            Dict with 'name', 'category', 'unit', 'icon' or None if unknown.
        """
        return YahooFetcher.COMMODITY_INFO.get(commodity.lower())

    @staticmethod
    def fetch_historical(commodity: str, period: str = "5y") -> pd.DataFrame:
        """Download historical OHLCV data for a commodity.

        Args:
            commodity: Commodity name (must be in SYMBOLS).
            period: Yahoo Finance period (e.g. '1y', '5y', 'max').

        Returns:
            DataFrame with columns date, open, high, low, close, volume (lowercase).

        Raises:
            ValueError: If commodity is unknown or no data is returned.
        """
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
            # Take only the first level of column names
            df.columns = [
                col[0] if isinstance(col, tuple) else col for col in df.columns
            ]

        # Remove any duplicate columns by keeping only the first occurrence
        df = df.loc[:, ~df.columns.duplicated()]

        # Standardize column names to lowercase
        df.columns = [str(col).lower().strip() for col in df.columns]

        print(f"Columns after flattening: {df.columns.tolist()}")

        # Keep only what we need
        columns_to_keep = ["date", "open", "high", "low", "close", "volume"]
        existing_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[existing_columns]

        # Remove rows with missing values
        df = df.dropna()

        print(f"Fetched {len(df)} data points")
        return df

    @staticmethod
    def list_commodities():
        """Return list of all supported commodities with metadata and symbol.

        Returns:
            List of dicts with 'id', 'name', 'category', 'unit', 'icon', 'symbol'.
        """
        return [
            {
                "id": key,
                **YahooFetcher.COMMODITY_INFO[key],
                "symbol": YahooFetcher.SYMBOLS[key],
            }
            for key in YahooFetcher.SYMBOLS.keys()
        ]
