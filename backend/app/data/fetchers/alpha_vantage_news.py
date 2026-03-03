"""Alpha Vantage news fetcher for commodity and market news with sentiment."""

import re
from typing import Dict, List

import requests


class AlphaVantageNewsFetcher:
    """Fetches commodity and market news from Alpha Vantage NEWS_SENTIMENT API."""

    BASE_URL = "https://www.alphavantage.co/query"
    
    # Map commodities to search keywords
    COMMODITY_KEYWORDS = {
        'gold': 'gold OR gold price OR gold market',
        'silver': 'silver OR silver price OR silver market',
        'crude_oil': 'crude oil OR oil price OR WTI OR petroleum',
        'natural_gas': 'natural gas OR gas price',
        'copper': 'copper OR copper price',
        'platinum': 'platinum OR platinum price',
        'palladium': 'palladium OR palladium price',
        'wheat': 'wheat OR wheat price OR grain',
        'corn': 'corn OR corn price OR maize',
        'soybeans': 'soybeans OR soybean price',
        'coffee': 'coffee OR coffee price',
        'sugar': 'sugar OR sugar price',
        'cotton': 'cotton OR cotton price',
    }
    
    @staticmethod
    def fetch_news(commodity: str, api_key: str, limit: int = 10) -> List[Dict]:
        """Fetch news articles for a specific commodity with sentiment.

        Args:
            commodity: Commodity identifier (e.g. 'gold', 'crude_oil').
            api_key: Alpha Vantage API key.
            limit: Maximum number of articles to return.

        Returns:
            List of article dicts with title, url, source, published_at,
            description, image_url, sentiment_label, sentiment_score.
        """
        # Get search keywords for commodity
        keywords = AlphaVantageNewsFetcher.COMMODITY_KEYWORDS.get(
            commodity.lower(), 
            f'{commodity} price'
        )
        
        # Try to use specific topics based on commodity
        if commodity in ['crude_oil', 'natural_gas']:
            topics = 'energy_transportation'
        elif commodity in ['wheat', 'corn', 'soybeans', 'coffee', 'sugar', 'cotton']:
            topics = 'economy_macro,manufacturing'
        else:
            topics = 'financial_markets,finance'
        
        params = {
            'function': 'NEWS_SENTIMENT',
            'topics': topics,
            'limit': 50,  # Fetch more to have better filtering
            'sort': 'LATEST',
            'apikey': api_key
        }
        
        try:
            response = requests.get(
                AlphaVantageNewsFetcher.BASE_URL, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                print(f"Alpha Vantage Error: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                print(f"Alpha Vantage Rate Limit: {data['Note']}")
                return []
            
            articles = []
            
            # Create search patterns for better matching
            commodity_patterns = {
                'gold': [r'\bgold\b', r'\bgold price\b', r'\bgold market\b'],
                'silver': [r'\bsilver\b', r'\bsilver price\b'],
                'crude_oil': [r'\boil\b', r'\bcrude\b', r'\bwti\b', r'\bpetroleum\b', r'\boil price\b'],
                'natural_gas': [r'\bnatural gas\b', r'\bgas price\b', r'\bgas market\b'],
                'copper': [r'\bcopper\b', r'\bcopper price\b'],
                'platinum': [r'\bplatinum\b'],
                'palladium': [r'\bpalladium\b'],
                'wheat': [r'\bwheat\b', r'\bwheat price\b', r'\bgrain\b'],
                'corn': [r'\bcorn\b', r'\bcorn price\b', r'\bmaize\b'],
                'soybeans': [r'\bsoybean\b', r'\bsoy\b'],
                'coffee': [r'\bcoffee\b', r'\bcoffee price\b'],
                'sugar': [r'\bsugar\b', r'\bsugar price\b'],
                'cotton': [r'\bcotton\b', r'\bcotton price\b']
            }
            
            patterns = commodity_patterns.get(commodity.lower(), [r'\b' + commodity.lower() + r'\b'])
            
            import re
            
            for item in data.get('feed', []):
                title = item.get('title', '').lower()
                summary = item.get('summary', '').lower()
                
                # Check if any pattern matches
                found = False
                for pattern in patterns:
                    if re.search(pattern, title) or re.search(pattern, summary):
                        found = True
                        break
                
                if found:
                    # Determine sentiment
                    sentiment_score = float(item.get('overall_sentiment_score', 0))
                    if sentiment_score > 0.15:
                        sentiment = 'bullish'
                        sentiment_label = '🟢 Bullish'
                    elif sentiment_score < -0.15:
                        sentiment = 'bearish'
                        sentiment_label = '🔴 Bearish'
                    else:
                        sentiment = 'neutral'
                        sentiment_label = '🟡 Neutral'
                    
                    articles.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'source': item.get('source'),
                        'published_at': item.get('time_published'),
                        'description': item.get('summary', '')[:200] + '...' if item.get('summary') else '',
                        'image_url': item.get('banner_image'),
                        'sentiment': sentiment,
                        'sentiment_label': sentiment_label,
                        'sentiment_score': sentiment_score
                    })
                
                if len(articles) >= limit:
                    break
            
            # If we found very few articles, add general finance news as fallback (no duplicates)
            seen_urls = {a.get('url') for a in articles if a.get('url')}
            if len(articles) < 3:
                print(f"Only found {len(articles)} articles for {commodity}, adding general finance news as fallback")
                for item in data.get('feed', []):
                    if len(articles) >= limit:
                        break
                    url = item.get('url')
                    if url and url in seen_urls:
                        continue
                    if url:
                        seen_urls.add(url)
                    sentiment_score = float(item.get('overall_sentiment_score', 0))
                    if sentiment_score > 0.15:
                        sentiment = 'bullish'
                        sentiment_label = '🟢 Bullish'
                    elif sentiment_score < -0.15:
                        sentiment = 'bearish'
                        sentiment_label = '🔴 Bearish'
                    else:
                        sentiment = 'neutral'
                        sentiment_label = '🟡 Neutral'
                    articles.append({
                        'title': item.get('title'),
                        'url': url,
                        'source': item.get('source'),
                        'published_at': item.get('time_published'),
                        'description': item.get('summary', '')[:250] + '...' if item.get('summary') else 'No description available.',
                        'image_url': item.get('banner_image'),
                        'sentiment': sentiment,
                        'sentiment_label': sentiment_label,
                        'sentiment_score': sentiment_score
                    })
            
            return articles[:limit]
            
        except Exception as e:
            print(f"Error fetching Alpha Vantage news: {str(e)}")
            return []
    
    @staticmethod
    def fetch_general_news(api_key: str, limit: int = 20) -> List[Dict]:
        """Fetch general financial/market news (not commodity-specific).

        Args:
            api_key: Alpha Vantage API key.
            limit: Maximum number of articles to return.

        Returns:
            List of article dicts with title, url, source, published_at,
            description, image_url, sentiment_label, sentiment_score.
        """
        params = {
            'function': 'NEWS_SENTIMENT',
            'topics': 'financial_markets,energy_transportation',
            'limit': limit,
            'apikey': api_key
        }
        
        try:
            response = requests.get(
                AlphaVantageNewsFetcher.BASE_URL, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                return []
            
            articles = []
            for item in data.get('feed', []):
                sentiment_score = float(item.get('overall_sentiment_score', 0))
                if sentiment_score > 0.15:
                    sentiment = 'bullish'
                    sentiment_label = '🟢 Bullish'
                elif sentiment_score < -0.15:
                    sentiment = 'bearish'
                    sentiment_label = '🔴 Bearish'
                else:
                    sentiment = 'neutral'
                    sentiment_label = '🟡 Neutral'
                articles.append({
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'source': item.get('source'),
                    'published_at': item.get('time_published'),
                    'description': item.get('summary', '')[:200] + '...' if item.get('summary') else '',
                    'image_url': item.get('banner_image'),
                    'sentiment': sentiment,
                    'sentiment_label': sentiment_label,
                    'sentiment_score': sentiment_score
                })
            return articles
            
        except Exception as e:
            print(f"Error fetching general news: {str(e)}")
            return []