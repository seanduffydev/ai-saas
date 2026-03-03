"""Pytest fixtures and shared mocks for backend tests."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Create mock app after patching so we get overrides; we need to import app
# and override its dependencies.
from fastapi.testclient import TestClient


def _make_mock_supabase(
    watchlist_data=None,
    portfolio_data=None,
    news_cache_data=None,
    auth_user=None,
):
    """Build a MagicMock Supabase client for table().select().eq().execute() etc."""
    mock = MagicMock()
    watchlist_data = watchlist_data or []
    portfolio_data = portfolio_data or []
    news_cache_data = news_cache_data or []

    # Table chain: .table(name).select(...).eq(...).order(...).execute() -> .data
    def table(name):
        t = MagicMock()
        t.select.return_value = t
        t.insert.return_value = t
        t.upsert.return_value = t
        t.delete.return_value = t
        t.eq.return_value = t
        t.neq.return_value = t
        t.order.return_value = t
        t.limit.return_value = t

        if name == "watchlist_preferences":
            t.execute.return_value = MagicMock(data=watchlist_data)
        elif name == "portfolio_positions":
            t.execute.return_value = MagicMock(data=portfolio_data)
        elif name == "news_cache":
            t.execute.return_value = MagicMock(data=news_cache_data)
        else:
            t.execute.return_value = MagicMock(data=[])
        return t

    mock.table.side_effect = table

    # Auth: get_user(credentials) returns object with .user
    if auth_user is None:
        auth_user = MagicMock()
        auth_user.id = "test-user-id"
        auth_user.email = "test@example.com"
    auth_response = MagicMock()
    auth_response.user = auth_user
    mock.auth.get_user.return_value = auth_response

    return mock


@pytest.fixture
def mock_supabase():
    """Default mock Supabase client."""
    return _make_mock_supabase()


@pytest.fixture
def mock_supabase_with_watchlist():
    return _make_mock_supabase(
        watchlist_data=[
            {
                "id": "1",
                "user_id": "u1",
                "commodity_id": "gold",
                "order_index": 0,
                "added_at": "2024-01-01T00:00:00Z",
            },
        ]
    )


@pytest.fixture
def mock_supabase_with_portfolio():
    return _make_mock_supabase(
        portfolio_data=[
            {
                "id": "pos-1",
                "user_id": "u1",
                "commodity": "Gold",
                "quantity": 10,
                "purchase_price": 1900.0,
                "purchase_date": "2024-01-01",
                "notes": None,
            }
        ]
    )


@pytest.fixture
def client(mock_supabase):
    """FastAPI TestClient with get_supabase overridden to return mock_supabase."""
    from app.core.database import get_supabase
    from app.main import app

    def override_get_supabase():
        return mock_supabase

    app.dependency_overrides[get_supabase] = override_get_supabase
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_supabase, None)


@pytest.fixture
def auth_headers(mock_supabase):
    """Bearer token for forecast; mock_supabase.auth.get_user accepts any token."""
    return {"Authorization": "Bearer fake-jwt-token"}


@pytest.fixture
def sample_historical_df():
    """Minimal DataFrame for YahooFetcher (date, open, high, low, close, volume)."""
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "open": [100.0] * 30,
            "high": [101.0] * 30,
            "low": [99.0] * 30,
            "close": [100.0 + i * 0.5 for i in range(30)],
            "volume": [1000] * 30,
        }
    )


@pytest.fixture
def sample_prices_and_dates():
    """List of prices and list of dates for forecast service tests."""
    base = datetime(2023, 1, 1)
    [(base + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    # dates from ForecastService are datetime objects when from Yahoo
    dates_as_dt = [base + timedelta(days=i) for i in range(30)]
    prices = [100.0 + i * 0.5 for i in range(30)]
    return prices, dates_as_dt


@pytest.fixture
def mock_yf_download(sample_historical_df):
    """Patch yfinance.download to return sample_historical_df."""
    with patch("yfinance.download", return_value=sample_historical_df.copy()) as m:
        yield m


@pytest.fixture
def mock_requests_get():
    """Patch requests.get for Alpha Vantage."""
    with patch("requests.get") as m:
        m.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "feed": [
                    {
                        "title": "Test article",
                        "url": "https://example.com/1",
                        "summary": "Summary",
                        "overall_sentiment_score": 0.5,
                        "overall_sentiment_label": "Neutral",
                    }
                ]
            },
            raise_for_status=MagicMock(),
        )
        yield m
