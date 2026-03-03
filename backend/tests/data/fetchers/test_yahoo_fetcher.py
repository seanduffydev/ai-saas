"""Tests for YahooFetcher."""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch

from app.data.fetchers.yahoo_fetcher import YahooFetcher


def test_get_symbol():
    assert YahooFetcher.get_symbol("gold") == "GC=F"
    assert YahooFetcher.get_symbol("GOLD") == "GC=F"
    assert YahooFetcher.get_symbol("unknown") is None


def test_get_info():
    info = YahooFetcher.get_info("gold")
    assert info["name"] == "Gold"
    assert info["category"] == "Metals"
    assert "unit" in info
    assert "icon" in info
    assert YahooFetcher.get_info("unknown") is None


def test_list_commodities():
    commodities = YahooFetcher.list_commodities()
    assert len(commodities) == 8
    ids = [c["id"] for c in commodities]
    assert "gold" in ids
    assert "silver" in ids
    for c in commodities:
        assert "name" in c
        assert "symbol" in c


def test_fetch_historical_success(sample_historical_df):
    """fetch_historical returns DataFrame with required columns."""
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=sample_historical_df.copy()):
        df = YahooFetcher.fetch_historical("gold", period="1y")
    assert "date" in df.columns
    assert "close" in df.columns
    assert len(df) == 30


def test_fetch_historical_unknown_commodity():
    with patch("app.data.fetchers.yahoo_fetcher.yf.download") as m:
        m.side_effect = ValueError("Unknown commodity")
        with pytest.raises(ValueError, match="Unknown commodity"):
            YahooFetcher.fetch_historical("unknown", period="1y")


def test_fetch_historical_empty_df():
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=pd.DataFrame()):
        with pytest.raises(ValueError, match="No data available"):
            YahooFetcher.fetch_historical("gold", period="1d")


def test_fetch_historical_with_datetime_index():
    """fetch_historical handles DataFrame with DatetimeIndex (yfinance-style)."""
    raw = pd.DataFrame(
        {
            "Open": [100.0] * 5,
            "High": [101.0] * 5,
            "Low": [99.0] * 5,
            "Close": [100.0 + i for i in range(5)],
            "Volume": [1000] * 5,
        },
        index=pd.date_range("2023-01-01", periods=5, freq="D"),
    )
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=raw):
        result = YahooFetcher.fetch_historical("gold", period="1y")
    assert "close" in result.columns
    assert len(result) == 5
