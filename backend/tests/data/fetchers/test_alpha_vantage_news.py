"""Tests for Alpha Vantage news fetcher."""

from unittest.mock import patch

from app.data.fetchers.alpha_vantage_news import AlphaVantageNewsFetcher


def test_commodity_keywords():
    assert "gold" in AlphaVantageNewsFetcher.COMMODITY_KEYWORDS
    assert "crude_oil" in AlphaVantageNewsFetcher.COMMODITY_KEYWORDS


def test_fetch_news_success():
    """fetch_news returns list of articles when API returns feed."""
    mock_data = {
        "feed": [
            {
                "title": "Gold price rises amid demand",
                "summary": "Gold market sees strong demand.",
                "overall_sentiment_score": 0.2,
                "url": "https://example.com/1",
                "source": "Reuters",
                "time_published": "20240101T120000",
                "banner_image": None,
            }
        ]
    }
    with patch("app.data.fetchers.alpha_vantage_news.requests.get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = mock_data
        m.return_value.raise_for_status = lambda: None
        articles = AlphaVantageNewsFetcher.fetch_news("gold", "fake-key", limit=10)
    assert len(articles) >= 1
    assert articles[0]["title"] == "Gold price rises amid demand"
    assert "sentiment" in articles[0] or "sentiment_label" in articles[0]


def test_fetch_news_api_error_returns_empty():
    with patch("app.data.fetchers.alpha_vantage_news.requests.get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = {"Error Message": "Invalid API key"}
        m.return_value.raise_for_status = lambda: None
        articles = AlphaVantageNewsFetcher.fetch_news("gold", "bad-key")
    assert articles == []


def test_fetch_news_rate_limit_returns_empty():
    with patch("app.data.fetchers.alpha_vantage_news.requests.get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = {"Note": "Rate limit exceeded"}
        m.return_value.raise_for_status = lambda: None
        articles = AlphaVantageNewsFetcher.fetch_news("gold", "key")
    assert articles == []


def test_fetch_news_exception_returns_empty():
    with patch(
        "app.data.fetchers.alpha_vantage_news.requests.get",
        side_effect=Exception("Network error"),
    ):
        articles = AlphaVantageNewsFetcher.fetch_news("gold", "key")
    assert articles == []


def test_fetch_general_news_success():
    mock_data = {
        "feed": [
            {
                "title": "Markets update",
                "summary": "Financial markets today.",
                "overall_sentiment_score": 0.0,
                "url": "https://example.com/1",
                "source": "Reuters",
                "time_published": "20240101T120000",
                "banner_image": None,
            }
        ]
    }
    with patch("app.data.fetchers.alpha_vantage_news.requests.get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = mock_data
        m.return_value.raise_for_status = lambda: None
        articles = AlphaVantageNewsFetcher.fetch_general_news("fake-key", limit=5)
    assert len(articles) == 1
    assert "sentiment_label" in articles[0]


def test_fetch_general_news_error_returns_empty():
    with patch("app.data.fetchers.alpha_vantage_news.requests.get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = {"Error Message": "Invalid key"}
        m.return_value.raise_for_status = lambda: None
        articles = AlphaVantageNewsFetcher.fetch_general_news("key")
    assert articles == []


def test_fetch_general_news_exception_returns_empty():
    with patch(
        "app.data.fetchers.alpha_vantage_news.requests.get",
        side_effect=Exception("Error"),
    ):
        articles = AlphaVantageNewsFetcher.fetch_general_news("key")
    assert articles == []
