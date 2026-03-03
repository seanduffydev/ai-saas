"""Tests for NewsCache."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.utils.news_cache import NewsCache


def test_get_cached_news_miss():
    """get_cached_news returns None when no cache entry."""
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.select.return_value.eq.return_value.execute
    chain.return_value = MagicMock(data=[])
    cache = NewsCache(mock_supabase)
    result = cache.get_cached_news("gold")
    assert result is None


def test_get_cached_news_hit():
    """get_cached_news returns articles when valid cache exists."""
    from datetime import timezone

    future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.select.return_value.eq.return_value
    chain.execute.return_value = MagicMock(
        data=[
            {
                "commodity": "gold",
                "articles": '[{"title":"Gold news"}]',
                "expires_at": future,
            }
        ]
    )
    cache = NewsCache(mock_supabase)
    result = cache.get_cached_news("gold")
    assert result is not None
    assert len(result) == 1
    assert result[0]["title"] == "Gold news"


def test_get_cached_news_expired_deletes_and_returns_none():
    """get_cached_news returns None and deletes when cache expired."""
    from datetime import timezone

    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.select.return_value.eq.return_value
    chain.execute.return_value = MagicMock(
        data=[{"commodity": "gold", "articles": "[]", "expires_at": past}]
    )
    delete_chain = mock_supabase.table.return_value.delete.return_value.eq.return_value
    delete_chain.execute.return_value = None
    cache = NewsCache(mock_supabase)
    result = cache.get_cached_news("gold")
    assert result is None
    mock_supabase.table.return_value.delete.return_value.eq.assert_called()


def test_cache_news():
    """cache_news calls upsert with serialized articles."""
    mock_supabase = MagicMock()
    cache = NewsCache(mock_supabase)
    cache.cache_news("gold", [{"title": "Test"}], source="alpha_vantage")
    mock_supabase.table.assert_called_with("news_cache")
    call_args = mock_supabase.table.return_value.upsert.call_args[0][0]
    assert call_args["commodity"] == "gold"
    assert "articles" in call_args
    assert call_args["article_count"] == 1


def test_clear_cache_commodity():
    """clear_cache with commodity deletes for that commodity."""
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.delete.return_value.eq.return_value
    chain.execute.return_value = None
    cache = NewsCache(mock_supabase)
    cache.clear_cache("gold")
    mock_supabase.table.return_value.delete.return_value.eq.assert_called_with(
        "commodity", "gold"
    )


def test_clear_cache_all():
    """clear_cache with None deletes all."""
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.delete.return_value.neq.return_value
    chain.execute.return_value = None
    cache = NewsCache(mock_supabase)
    cache.clear_cache(None)
    mock_supabase.table.return_value.delete.return_value.neq.assert_called_with(
        "commodity", ""
    )


def test_get_cache_stats():
    """get_cache_stats returns total_cached_commodities and cache_entries."""
    from datetime import timezone

    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    mock_supabase = MagicMock()
    chain = mock_supabase.table.return_value.select.return_value.execute
    chain.return_value = MagicMock(
        data=[
            {
                "commodity": "gold",
                "article_count": 5,
                "fetched_at": "...",
                "expires_at": future,
            },
        ]
    )
    cache = NewsCache(mock_supabase)
    stats = cache.get_cache_stats()
    assert stats["total_cached_commodities"] == 1
    assert len(stats["cache_entries"]) == 1
    assert stats["cache_entries"][0]["commodity"] == "gold"


def test_get_cache_stats_exception_returns_error():
    """get_cache_stats returns error dict on exception."""
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.execute.side_effect = (
        Exception("DB error")
    )
    cache = NewsCache(mock_supabase)
    stats = cache.get_cache_stats()
    assert "error" in stats
