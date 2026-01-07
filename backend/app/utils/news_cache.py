from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class NewsCache:
    """Manage news caching in Supabase"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.cache_duration_hours = 4  # Cache for 4 hours
    
    def get_cached_news(self, commodity: str) -> Optional[List[Dict]]:
        """
        Get cached news if available and not expired
        
        Returns:
            List of articles if cache is valid, None if cache miss/expired
        """
        try:
            # Query cache
            result = self.supabase.table('news_cache').select('*').eq('commodity', commodity).execute()
            
            if not result.data or len(result.data) == 0:
                print(f"Cache miss for {commodity}")
                return None
            
            cache_entry = result.data[0]
            
            # Check if expired
            expires_at = datetime.fromisoformat(cache_entry['expires_at'].replace('Z', '+00:00'))
            now = datetime.now(expires_at.tzinfo)
            
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
        """
        Cache news articles
        
        Args:
            commodity: Commodity name
            articles: List of article dictionaries
            source: API source name
        """
        try:
            expires_at = datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
            
            cache_data = {
                'commodity': commodity,
                'articles': json.dumps(articles) if isinstance(articles, list) else articles,
                'source': source,
                'fetched_at': datetime.utcnow().isoformat(),
                'expires_at': expires_at.isoformat(),
                'article_count': len(articles)
            }
            
            # Upsert (insert or update if exists)
            self.supabase.table('news_cache').upsert(cache_data).execute()
            
            print(f"Cached {len(articles)} articles for {commodity} (expires at {expires_at.strftime('%H:%M:%S')})")
            
        except Exception as e:
            print(f"Error caching news: {str(e)}")
    
    def clear_cache(self, commodity: Optional[str] = None):
        """
        Clear cache for a specific commodity or all
        
        Args:
            commodity: Specific commodity to clear, or None for all
        """
        try:
            if commodity:
                self.supabase.table('news_cache').delete().eq('commodity', commodity).execute()
                print(f"Cleared cache for {commodity}")
            else:
                self.supabase.table('news_cache').delete().neq('commodity', '').execute()
                print("Cleared all cache")
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            result = self.supabase.table('news_cache').select('commodity, article_count, fetched_at, expires_at').execute()
            
            stats = {
                'total_cached_commodities': len(result.data),
                'cache_entries': []
            }
            
            for entry in result.data:
                expires_at = datetime.fromisoformat(entry['expires_at'].replace('Z', '+00:00'))
                now = datetime.now(expires_at.tzinfo)
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