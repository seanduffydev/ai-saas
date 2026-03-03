"""News cache utilities using Supabase for persistence."""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional


class NewsCache:
    """Manages news article caching in Supabase with configurable TTL."""

    def __init__(self, supabase_client):
        """Initialize the cache with a Supabase client.

        Args:
            supabase_client: Supabase Client instance for table access.
        """
        self.supabase = supabase_client
        self.cache_duration_hours = 4

    def get_cached_news(self, commodity: str) -> Optional[List[Dict]]:
        """Return cached news for a commodity if present and not expired.

        Args:
            commodity: Commodity identifier (e.g. 'gold', 'all').

        Returns:
            List of article dicts if cache hit and valid; None on miss or expiry.
        """
        try:
            # Query cache
            result = self.supabase.table('news_cache').select('*').eq('commodity', commodity).execute()
            
            if not result.data or len(result.data) == 0:
                print(f"Cache miss for {commodity}")
                return None
            
            cache_entry = result.data[0]
            
            # Check if expired (use UTC for both so comparison is correct)
            raw = cache_entry['expires_at'].replace('Z', '+00:00')
            expires_at = datetime.fromisoformat(raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            
            if now > expires_at:
                print(f"Cache expired for {commodity}")
                # Delete expired cache
                self.supabase.table('news_cache').delete().eq('commodity', commodity).execute()
                return None
            
            print(f"Cache hit for {commodity} (expires in {(expires_at - now).seconds // 60} minutes)")
            
            # Parse articles if they're stored as JSON string
            articles = cache_entry['articles']
            if isinstance(articles, str):
                articles = json.loads(articles)
            
            return articles
            
        except Exception as e:
            print(f"Error reading cache: {str(e)}")
            return None
    
    def cache_news(self, commodity: str, articles: List[Dict], source: str = 'alpha_vantage'):
        """Store news articles in cache for the given commodity.

        Args:
            commodity: Commodity identifier to key the cache.
            articles: List of article dicts to store.
            source: Label for the API source (e.g. 'alpha_vantage').
        """
        try:
            now_utc = datetime.now(timezone.utc)
            expires_at = now_utc + timedelta(hours=self.cache_duration_hours)
            
            cache_data = {
                'commodity': commodity,
                'articles': json.dumps(articles) if isinstance(articles, list) else articles,
                'source': source,
                'fetched_at': now_utc.isoformat(),
                'expires_at': expires_at.isoformat(),
                'article_count': len(articles)
            }
            
            # Upsert (insert or update if exists)
            self.supabase.table('news_cache').upsert(cache_data).execute()
            
            print(f"Cached {len(articles)} articles for {commodity} (expires at {expires_at.strftime('%H:%M:%S')})")
            
        except Exception as e:
            print(f"Error caching news: {str(e)}")
    
    def clear_cache(self, commodity: Optional[str] = None):
        """Remove cached entries for one commodity or all.

        Args:
            commodity: Commodity to clear, or None to clear all entries.
        """
        try:
            if commodity:
                self.supabase.table('news_cache').delete().eq('commodity', commodity).execute()
                print(f"Cleared cache for {commodity}")
            else:
                # Delete all: non-empty commodity first, then rows where commodity is null
                self.supabase.table('news_cache').delete().neq('commodity', '').execute()
                try:
                    self.supabase.table('news_cache').delete().is_('commodity', 'null').execute()
                except Exception:
                    pass
                print("Cleared all cache")
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict:
        """Return summary statistics for cached news.

        Returns:
            Dict with 'total_cached_commodities', 'cache_entries' (list of
            per-commodity stats). On error, may include 'error' key.
        """
        try:
            result = self.supabase.table('news_cache').select('commodity, article_count, fetched_at, expires_at').execute()
            
            stats = {
                'total_cached_commodities': len(result.data),
                'cache_entries': []
            }
            
            for entry in result.data:
                raw = entry['expires_at'].replace('Z', '+00:00')
                expires_at = datetime.fromisoformat(raw)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                is_valid = now < expires_at
                
                stats['cache_entries'].append({
                    'commodity': entry['commodity'],
                    'articles': entry['article_count'],
                    'valid': is_valid,
                    'expires_in_minutes': (expires_at - now).seconds // 60 if is_valid else 0
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}