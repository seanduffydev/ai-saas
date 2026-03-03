"""News endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.api.v1.deps import get_supabase
from app.config import settings
from app.data.fetchers.alpha_vantage_news import AlphaVantageNewsFetcher
from app.utils.news_cache import NewsCache

router = APIRouter()


@router.get("/api/news/{commodity}")
def get_commodity_news(
    commodity: str,
    limit: int = 10,
    force_refresh: bool = False,
    supabase: Client = Depends(get_supabase),
):
    """Get news articles for a specific commodity.

    Uses 4-hour caching to reduce API calls. News is fetched from Alpha Vantage
    and includes sentiment analysis (Bullish/Neutral/Bearish).

    Args:
        commodity: Commodity name (e.g., 'gold', 'silver')
        limit: Maximum number of articles to return (default: 10)
        force_refresh: Skip cache and fetch fresh data (default: False)
        supabase: Database client (injected by dependency)

    Returns:
        News articles with metadata and sentiment scores

    Raises:
        HTTPException: 500 if news fetching fails
    """
    try:
        cache = NewsCache(supabase)

        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_articles = cache.get_cached_news(commodity)
            if cached_articles:
                return {
                    "commodity": commodity,
                    "articles": cached_articles[:limit],
                    "count": len(cached_articles[:limit]),
                    "source": "cache",
                    "cached": True,
                }

        # Cache miss or force refresh - fetch from API
        print(f"Fetching fresh news for {commodity} from Alpha Vantage...")
        articles = AlphaVantageNewsFetcher.fetch_news(
            commodity=commodity, api_key=settings.alpha_vantage_api_key, limit=limit
        )

        # Cache the results
        if articles:
            cache.cache_news(commodity, articles, source="alpha_vantage")

        return {
            "commodity": commodity,
            "articles": articles,
            "count": len(articles),
            "source": "alpha_vantage",
            "cached": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")


@router.get("/api/news")
def get_general_news(
    limit: int = 20,
    force_refresh: bool = False,
    supabase: Client = Depends(get_supabase),
):
    """Get general commodity market news.

    Uses 4-hour caching. Returns broad market news across all commodities.

    Args:
        limit: Maximum number of articles (default: 20)
        force_refresh: Skip cache and fetch fresh data (default: False)
        supabase: Database client (injected by dependency)

    Returns:
        General news articles with sentiment analysis

    Raises:
        HTTPException: 500 if news fetching fails
    """
    try:
        # Use 'all' as the cache key for general news
        cache = NewsCache(supabase)

        # Try cache first
        if not force_refresh:
            cached_articles = cache.get_cached_news("all")
            if cached_articles:
                return {
                    "articles": cached_articles[:limit],
                    "count": len(cached_articles[:limit]),
                    "source": "cache",
                    "cached": True,
                }

        # Fetch fresh
        print("Fetching fresh general news from Alpha Vantage...")
        articles = AlphaVantageNewsFetcher.fetch_general_news(
            api_key=settings.alpha_vantage_api_key, limit=limit
        )

        # Cache
        if articles:
            cache.cache_news("all", articles, source="alpha_vantage")

        return {
            "articles": articles,
            "count": len(articles),
            "source": "alpha_vantage",
            "cached": False,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch general news: {str(e)}"
        )


@router.get("/api/news/cache/stats")
def get_cache_stats(supabase: Client = Depends(get_supabase)):
    """Get news cache statistics (admin endpoint).

    Returns information about cached news including:
    - Number of cached commodities
    - Cache hit rates
    - Storage usage
    - Expiration times

    Args:
        supabase: Database client (injected by dependency)

    Returns:
        Cache statistics dictionary

    Raises:
        HTTPException: 500 if stats retrieval fails
    """
    try:
        cache = NewsCache(supabase)
        stats = cache.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/api/news/cache/clear")
def clear_news_cache(
    commodity: str | None = None, supabase: Client = Depends(get_supabase)
):
    """Clear news cache (admin endpoint).

    Args:
        commodity: Specific commodity to clear, or None for all (optional)
        supabase: Database client (injected by dependency)

    Returns:
        Success message

    Raises:
        HTTPException: 500 if cache clearing fails
    """
    try:
        cache = NewsCache(supabase)
        cache.clear_cache(commodity)
        msg = f"Cache cleared for {commodity}" if commodity else "Cache cleared for all"
        return {"message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
