import requests
import re
from typing import List, Dict

class AlphaVantageNewsFetcher:
    """Fetch commodity news from Alpha Vantage (Production-Safe!)"""
    
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
        """Fetch news for a specific commodity"""
        
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
            
            # If we found very few articles, relax the filter
            if len(articles) < 3:
                print(f"Only found {len(articles)} articles for {commodity}, fetching general finance news")
                # Return general finance news as fallback
                for item in data.get('feed', [])[:limit]:
                    sentiment_score = float(item.get('overall_sentiment_score', 0))
                    if sentiment_score > 0.15:
                        sentiment_label = '🟢 Bullish'
                    elif sentiment_score < -0.15:
                        sentiment_label = '🔴 Bearish'
                    else:
                        sentiment_label = '🟡 Neutral'
                    
                    articles.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'source': item.get('source'),
                        'published_at': item.get('time_published'),
                        'description': item.get('summary', '')[:250] + '...' if item.get('summary') else 'No description available.',
                        'image_url': item.get('banner_image'),
                        'sentiment_label': sentiment_label,
                        'sentiment_score': sentiment_score
                    })
            
            return articles[:limit]
            
        except Exception as e:
            print(f"Error fetching Alpha Vantage news: {str(e)}")
            return []
    
    @staticmethod
    def fetch_general_news(api_key: str, limit: int = 20) -> List[Dict]:
        """Fetch general commodity market news"""
        
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
                    sentiment_label = '🟢 Bullish'
                elif sentiment_score < -0.15:
                    sentiment_label = '🔴 Bearish'
                else:
                    sentiment_label = '🟡 Neutral'
                
                articles.append({
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'source': item.get('source'),
                    'published_at': item.get('time_published'),
                    'description': item.get('summary', '')[:200] + '...' if item.get('summary') else '',
                    'image_url': item.get('banner_image'),
                    'sentiment_label': sentiment_label,
                    'sentiment_score': sentiment_score
                })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching general news: {str(e)}")
            return []