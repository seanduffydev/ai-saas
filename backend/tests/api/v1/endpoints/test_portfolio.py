"""Tests for portfolio API endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


def test_get_portfolio_empty(client: TestClient):
    """GET /api/portfolio returns empty list when no positions."""
    response = client.get("/api/portfolio?user_id=user-1")
    assert response.status_code == 200
    assert response.json() == []


def test_get_portfolio_with_positions(client: TestClient, mock_supabase_with_portfolio):
    """GET /api/portfolio returns enriched positions."""
    from app.main import app
    from app.core.database import get_supabase
    app.dependency_overrides[get_supabase] = lambda: mock_supabase_with_portfolio
    with patch("app.services.portfolio_service.yf.download") as mock_download:
        import pandas as pd
        mock_download.return_value = pd.DataFrame({"Close": [1950.0]})
        with TestClient(app) as c:
            response = c.get("/api/portfolio?user_id=u1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["commodity"] == "Gold"
    assert "current_price" in data[0]
    app.dependency_overrides.pop(get_supabase, None)


def test_add_position(client: TestClient):
    """POST /api/portfolio adds position."""
    response = client.post(
        "/api/portfolio?user_id=user-1",
        json={
            "commodity": "Gold",
            "quantity": 10.0,
            "purchase_price": 1900.0,
            "purchase_date": "2024-01-15",
            "notes": "Test",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_delete_position(client: TestClient):
    """DELETE /api/portfolio/{id} returns success."""
    response = client.delete("/api/portfolio/some-uuid?user_id=user-1")
    assert response.status_code == 200
    assert "message" in response.json()
