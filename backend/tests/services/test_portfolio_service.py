"""Tests for PortfolioService."""

from unittest.mock import patch

import pandas as pd

from app.services.portfolio_service import PortfolioService


def test_get_ticker_for_commodity():
    """get_ticker_for_commodity returns correct symbol."""
    assert PortfolioService.get_ticker_for_commodity("Gold") == "GC=F"
    assert PortfolioService.get_ticker_for_commodity("Silver") == "SI=F"
    assert PortfolioService.get_ticker_for_commodity("Unknown") == ""


def test_get_current_price_success():
    """get_current_price returns float when yf returns data."""
    df = pd.DataFrame({"Close": [1950.0]})
    with patch("app.services.portfolio_service.yf.download", return_value=df):
        price = PortfolioService.get_current_price("Gold")
    assert price == 1950.0


def test_get_current_price_empty_df():
    """get_current_price returns None when no data."""
    with patch(
        "app.services.portfolio_service.yf.download", return_value=pd.DataFrame()
    ):
        price = PortfolioService.get_current_price("Gold")
    assert price is None


def test_get_current_price_unknown_commodity():
    """get_current_price returns None for unknown commodity."""
    price = PortfolioService.get_current_price("UnknownCommodity")
    assert price is None


def test_get_current_price_exception():
    """get_current_price returns None on exception."""
    with patch(
        "app.services.portfolio_service.yf.download",
        side_effect=Exception("Network error"),
    ):
        price = PortfolioService.get_current_price("Gold")
    assert price is None


def test_calculate_position_metrics_with_price():
    """calculate_position_metrics returns current_value, profit_loss, percent."""
    result = PortfolioService.calculate_position_metrics(
        quantity=10.0, purchase_price=100.0, current_price=110.0
    )
    assert result["current_value"] == 1100.0
    assert result["profit_loss"] == 100.0
    assert result["profit_loss_percent"] == 10.0


def test_calculate_position_metrics_none_price():
    """calculate_position_metrics returns None metrics when current_price is None."""
    result = PortfolioService.calculate_position_metrics(
        quantity=10.0, purchase_price=100.0, current_price=None
    )
    assert result["current_value"] is None
    assert result["profit_loss"] is None
    assert result["profit_loss_percent"] is None


def test_enrich_position_with_current_data():
    """enrich_position_with_current_data adds current_price and metrics."""
    position = {
        "id": "1",
        "commodity": "Gold",
        "quantity": 10.0,
        "purchase_price": 1900.0,
    }
    with patch.object(PortfolioService, "get_current_price", return_value=1950.0):
        enriched = PortfolioService.enrich_position_with_current_data(position)
    assert enriched["current_price"] == 1950.0
    assert enriched["current_value"] == 19500.0
    assert enriched["profit_loss"] == 500.0
