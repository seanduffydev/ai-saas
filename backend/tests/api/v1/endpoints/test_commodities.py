"""Tests for commodities API endpoints."""

import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime

from fastapi.testclient import TestClient


def test_get_commodities(client: TestClient):
    """GET /api/commodities returns list of commodities."""
    response = client.get("/api/commodities")
    assert response.status_code == 200
    data = response.json()
    assert "commodities" in data
    assert len(data["commodities"]) == 8
    assert any(c["id"] == "gold" for c in data["commodities"])


def test_get_commodity_info(client: TestClient):
    """GET /api/commodities/gold returns commodity info."""
    response = client.get("/api/commodities/gold")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "gold"
    assert data["name"] == "Gold"
    assert data["symbol"] == "GC=F"


def test_get_commodity_info_404(client: TestClient):
    """GET /api/commodities/unknown returns 404."""
    response = client.get("/api/commodities/unknown_commodity_xyz")
    assert response.status_code == 404


def test_get_prices(client: TestClient, sample_historical_df):
    """GET /api/prices/gold returns price history."""
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", return_value=sample_historical_df.copy()):
        response = client.get("/api/prices/gold?period=1y")
    assert response.status_code == 200
    data = response.json()
    assert data["commodity"] == "gold"
    assert "data" in data
    assert data["data_points"] == 30
    assert len(data["data"]) == 30


def test_get_prices_unknown_commodity_500(client: TestClient):
    """GET /api/prices/unknown returns 500 when fetch fails."""
    with patch("app.data.fetchers.yahoo_fetcher.yf.download", side_effect=ValueError("Unknown")):
        response = client.get("/api/prices/unknown_ticker?period=1y")
    assert response.status_code == 500
