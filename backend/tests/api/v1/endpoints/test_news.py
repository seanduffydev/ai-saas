"""Tests for news API endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_get_commodity_news_fresh(client: TestClient):
    """GET /api/news/gold returns articles from API when no cache."""
    mock_articles = [
        {"title": "Gold rises", "url": "https://x.com", "sentiment_label": "Bullish"}
    ]
    with patch(
        "app.api.v1.endpoints.news.AlphaVantageNewsFetcher.fetch_news",
        return_value=mock_articles,
    ):
        response = client.get("/api/news/gold?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Gold rises"


def test_get_general_news(client: TestClient):
    """GET /api/news returns general news."""
    mock_articles = [{"title": "Markets", "url": "https://x.com"}]
    with patch(
        "app.api.v1.endpoints.news.AlphaVantageNewsFetcher.fetch_general_news",
        return_value=mock_articles,
    ):
        response = client.get("/api/news?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert len(data["articles"]) == 1


def test_get_news_cache_stats(client: TestClient):
    """GET /api/news/cache/stats returns stats."""
    response = client.get("/api/news/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert (
        "total_cached_commodities" in data or "cache_entries" in data or "error" in data
    )


def test_clear_news_cache(client: TestClient):
    """POST /api/news/cache/clear clears cache."""
    response = client.post("/api/news/cache/clear")
    assert response.status_code == 200
    assert "message" in response.json()


def test_clear_news_cache_commodity(client: TestClient):
    """POST /api/news/cache/clear?commodity=gold clears for commodity."""
    response = client.post("/api/news/cache/clear?commodity=gold")
    assert response.status_code == 200
