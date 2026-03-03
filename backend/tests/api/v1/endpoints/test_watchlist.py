"""Tests for watchlist API endpoints."""

from fastapi.testclient import TestClient


def test_get_watchlist_empty(client: TestClient, auth_headers):
    """GET /api/watchlist returns empty list when no items."""
    response = client.get("/api/watchlist", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_watchlist_with_items(
    client: TestClient, auth_headers, mock_supabase_with_watchlist
):
    """GET /api/watchlist returns user items."""
    from app.core.database import get_supabase
    from app.main import app

    app.dependency_overrides[get_supabase] = lambda: mock_supabase_with_watchlist
    with TestClient(app) as c:
        response = c.get("/api/watchlist", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["commodity_id"] == "gold"
    app.dependency_overrides.pop(get_supabase, None)


def test_add_to_watchlist(client: TestClient, auth_headers):
    """POST /api/watchlist adds commodity."""
    response = client.post(
        "/api/watchlist",
        headers=auth_headers,
        json={"commodity_id": "silver"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "added" in data["message"].lower() or "commodity" in data["message"].lower()


def test_remove_from_watchlist(client: TestClient, auth_headers):
    """DELETE /api/watchlist/gold removes commodity."""
    response = client.delete("/api/watchlist/gold", headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()


def test_initialize_watchlist_empty(client: TestClient, auth_headers):
    """POST /api/watchlist/initialize creates default items."""
    response = client.post(
        "/api/watchlist/initialize",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "message" in data


def test_initialize_watchlist_already_has_items(
    client: TestClient, auth_headers, mock_supabase_with_watchlist
):
    """POST /api/watchlist/initialize when user has items returns existing."""
    from app.core.database import get_supabase
    from app.main import app

    app.dependency_overrides[get_supabase] = lambda: mock_supabase_with_watchlist
    with TestClient(app) as c:
        response = c.post("/api/watchlist/initialize", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert (
        "already initialized" in data["message"].lower()
        or len(data.get("data", [])) >= 1
    )
    app.dependency_overrides.pop(get_supabase, None)
