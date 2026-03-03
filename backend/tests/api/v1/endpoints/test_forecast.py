"""Tests for forecast API endpoints."""

import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime
from fastapi.testclient import TestClient


@pytest.fixture
def small_historical_df():
    """Small DataFrame for fast forecast training."""
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": [100.0] * 50,
        "high": [101.0] * 50,
        "low": [99.0] * 50,
        "close": [100.0 + i * 0.3 for i in range(50)],
        "volume": [1000] * 50,
    })


def test_forecast_requires_auth(client: TestClient):
    """POST /api/forecast without token returns 401."""
    response = client.post(
        "/api/forecast",
        json={
            "commodity": "gold",
            "forecast_days": 5,
            "window_size": 10,
            "period": "1y",
        },
    )
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 when no auth header


def test_forecast_success(client: TestClient, auth_headers, small_historical_df):
    """POST /api/forecast with auth returns predictions."""
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=small_historical_df):
        response = client.post(
            "/api/forecast",
            json={
                "commodity": "gold",
                "forecast_days": 5,
                "window_size": 10,
                "period": "1y",
            },
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["commodity"] == "gold"
    assert "historical_data" in data
    assert "predictions" in data
    assert "metrics" in data
    assert "model_info" in data
    assert len(data["predictions"]) == 5


def test_forecast_compare_success(client: TestClient, auth_headers, small_historical_df):
    """POST /api/forecast-compare returns both model predictions."""
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=small_historical_df):
        response = client.post(
            "/api/forecast-compare",
            json={
                "commodity": "gold",
                "forecast_days": 5,
                "window_size": 10,
                "period": "1y",
            },
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["commodity"] == "gold"
    assert "lstm_predictions" in data
    assert "transformer_predictions" in data
    assert "model_comparison" in data
