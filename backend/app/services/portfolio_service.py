"""Portfolio management business logic."""

from typing import Any

import pandas as pd
import yfinance as yf


class PortfolioService:
    """Service for portfolio operations."""

    # Ticker mapping (display names as in portfolio UI)
    TICKER_MAP = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Crude Oil": "CL=F",
        "Copper": "HG=F",
        "Natural Gas": "NG=F",
        "Platinum": "PL=F",
        "Wheat": "ZW=F",
        "Corn": "ZC=F",
        "Soybeans": "ZS=F",
    }

    @classmethod
    def get_ticker_for_commodity(cls, commodity: str) -> str:
        """Map commodity name to Yahoo Finance ticker.

        Args:
            commodity: Commodity name (e.g., 'Gold', 'Silver')

        Returns:
            Yahoo Finance ticker symbol (e.g., 'GC=F')
        """
        return cls.TICKER_MAP.get(commodity, "")

    @classmethod
    def get_current_price(cls, commodity: str) -> float | None:
        """Fetch current market price for a commodity.

        Args:
            commodity: Commodity name

        Returns:
            Current price or None if fetch fails
        """
        try:
            ticker = cls.get_ticker_for_commodity(commodity)
            if not ticker:
                return None

            df = yf.download(ticker, period="1d", progress=False)
            if df.empty:
                return None

            # Handle MultiIndex columns or different casing (yfinance varies)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    col[0] if isinstance(col, tuple) else col for col in df.columns
                ]
            df.columns = [str(c).lower().strip() for c in df.columns]
            close_col = "close" if "close" in df.columns else "Close"
            if close_col not in df.columns:
                return None
            return float(df[close_col].iloc[-1].item())
        except Exception as e:
            print(f"Error fetching price for {commodity}: {e}")
            return None

    @staticmethod
    def calculate_position_metrics(
        quantity: float, purchase_price: float, current_price: float | None
    ) -> dict[str, float | None]:
        """Calculate profit/loss metrics for a position.

        Args:
            quantity: Number of units
            purchase_price: Price per unit at purchase
            current_price: Current market price (optional)

        Returns:
            Dictionary with calculated metrics
        """
        purchase_value = quantity * purchase_price

        if current_price is None:
            return {
                "current_value": None,
                "profit_loss": None,
                "profit_loss_percent": None,
            }

        current_value = quantity * current_price
        profit_loss = current_value - purchase_value
        profit_loss_percent = (profit_loss / purchase_value) * 100

        return {
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent,
        }

    @classmethod
    def enrich_position_with_current_data(
        cls, position: dict[str, Any]
    ) -> dict[str, Any]:
        """Enrich a portfolio position with current market data.

        Args:
            position: Position data from database

        Returns:
            Position with current price and calculated metrics
        """
        current_price = cls.get_current_price(position["commodity"])

        quantity = float(position["quantity"])
        purchase_price = float(position["purchase_price"])

        metrics = cls.calculate_position_metrics(
            quantity, purchase_price, current_price
        )

        return {**position, "current_price": current_price, **metrics}
