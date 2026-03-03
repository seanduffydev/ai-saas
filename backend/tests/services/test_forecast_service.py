"""Tests for ForecastService."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from app.services.forecast_service import ForecastService


def test_fetch_historical_data_mocked():
    """fetch_historical_data returns prices and dates from YahooFetcher."""
    df = pd.DataFrame({
        "date": [datetime(2024, 1, 1), datetime(2024, 1, 2)],
        "close": [100.0, 101.0],
    })
    with patch("app.services.forecast_service.YahooFetcher") as MockYahoo:
        MockYahoo.fetch_historical.return_value = df
        prices, dates = ForecastService.fetch_historical_data("gold", "1y")
    assert prices == [100.0, 101.0]
    assert len(dates) == 2


def test_generate_future_dates():
    """generate_future_dates returns correct date strings."""
    last = datetime(2024, 1, 10)
    result = ForecastService.generate_future_dates(last, 3)
    assert result == ["2024-01-11", "2024-01-12", "2024-01-13"]


def test_format_historical_data():
    """format_historical_data returns list of dicts with date and price."""
    prices = [100.0, 101.0, 102.0]
    dates = [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)]
    result = ForecastService.format_historical_data(prices, dates, display_count=2)
    assert len(result) == 2
    assert result[0]["date"] == "2024-01-02"
    assert result[0]["price"] == 101.0
    assert result[1]["date"] == "2024-01-03"
    assert result[1]["price"] == 102.0


def test_format_historical_data_count_larger_than_data():
    """format_historical_data uses all data when display_count > len(prices)."""
    prices = [100.0, 101.0]
    dates = [datetime(2024, 1, 1), datetime(2024, 1, 2)]
    result = ForecastService.format_historical_data(prices, dates, display_count=100)
    assert len(result) == 2


def test_format_predictions():
    """format_predictions returns list with date, price, day."""
    preds = [105.0, 106.0]
    dates = ["2024-02-01", "2024-02-02"]
    result = ForecastService.format_predictions(preds, dates)
    assert len(result) == 2
    assert result[0]["date"] == "2024-02-01"
    assert result[0]["price"] == 105.0
    assert result[0]["day"] == 1
    assert result[1]["day"] == 2


def test_calculate_comparison_metrics():
    """calculate_comparison_metrics returns lstm_avg, transformer_avg, difference."""
    lstm = [100.0, 102.0]
    trans = [101.0, 103.0]
    result = ForecastService.calculate_comparison_metrics(lstm, trans)
    assert result["lstm_avg_price"] == 101.0
    assert result["transformer_avg_price"] == 102.0
    assert result["difference"] == 1.0


def test_train_lstm_model():
    """train_lstm_model returns forecaster and metrics."""
    prices = [100.0 + i * 0.5 for i in range(25)]
    forecaster, metrics = ForecastService.train_lstm_model(
        prices, window_size=5, forecast_days=3, epochs=2
    )
    assert forecaster is not None
    assert "final_loss" in metrics
    assert metrics["epochs"] == 2


def test_train_transformer_model():
    """train_transformer_model returns forecaster and metrics."""
    prices = [100.0 + i * 0.5 for i in range(25)]
    forecaster, metrics = ForecastService.train_transformer_model(
        prices, window_size=5, forecast_days=3, epochs=2
    )
    assert forecaster is not None
    assert "final_loss" in metrics
    assert metrics["epochs"] == 2
