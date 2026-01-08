from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta, date 
from supabase import create_client
from decimal import Decimal
import pandas as pd
import numpy as np
import yfinance as yf

from app.data.fetchers.yahoo_fetcher import YahooFetcher
from app.models.lstm_forecaster import LSTMForecaster
from app.models.transformer_forecaster import TransformerForecaster
from app.data.fetchers.alpha_vantage_news import AlphaVantageNewsFetcher
from app.utils.news_cache import NewsCache
from app.config import settings

app = FastAPI(title="Commodity Forecasting Lab", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-saas-fawn-kappa.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase
supabase = create_client(settings.supabase_url, settings.supabase_key)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Models
class ForecastRequest(BaseModel):
    commodity: str
    forecast_days: int = 30
    window_size: int = 60
    period: str = '2y'

class ForecastResponse(BaseModel):
    commodity: str
    commodity_info: dict
    historical_data: List[dict]
    predictions: List[dict]
    metrics: dict
    model_info: dict

class PortfolioPosition(BaseModel):
    commodity: str
    quantity: float
    purchase_price: float
    purchase_date: date
    notes: Optional[str] = None

class PortfolioPositionResponse(BaseModel):
    id: str
    user_id: str
    commodity: str
    quantity: float
    purchase_price: float
    purchase_date: date
    notes: Optional[str]
    current_price: Optional[float]
    current_value: Optional[float]
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]

class WatchlistItem(BaseModel):
    commodity_id: str

class WatchlistItemResponse(BaseModel):
    id: str
    user_id: str
    commodity_id: str
    order_index: int
    added_at: str   

# Helper Function

def get_ticker_for_commodity(commodity: str) -> str:
    """Map commodity name to Yahoo Finance ticker"""
    ticker_map = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Crude Oil": "CL=F",
        "Copper": "HG=F",
        "Natural Gas": "NG=F",
        "Platinum": "PL=F",
        "Wheat": "ZW=F",
        "Corn": "ZC=F"
    }
    return ticker_map.get(commodity, "")

# Routes
@app.get("/")
def root():
    return {
        "message": "Commodity Forecasting Lab API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/commodities")
def get_commodities():
    """Get list of available commodities"""
    commodities = YahooFetcher.list_commodities()
    return {"commodities": commodities}

@app.get("/api/commodities/{commodity}")
def get_commodity_info(commodity: str):
    """Get information about a specific commodity"""
    info = YahooFetcher.get_info(commodity)
    if not info:
        raise HTTPException(status_code=404, detail=f"Commodity not found")
    
    symbol = YahooFetcher.get_symbol(commodity)
    return {"id": commodity, **info, "symbol": symbol}

@app.get("/api/prices/{commodity}")
def get_prices(commodity: str, period: str = '1y'):
    """Fetch historical prices"""
    try:
        df = YahooFetcher.fetch_historical(commodity, period)
        
        data = []
        for i in range(len(df)):
            row = df.iloc[i]
            # Handle date - it might already be a string or a datetime
            date_val = row['date']
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            data.append({
                'date': date_str,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']) if 'volume' in row and not pd.isna(row['volume']) else 0
            })
        
        info = YahooFetcher.get_info(commodity)
        return {
            "commodity": commodity,
            "commodity_info": info,
            "period": period,
            "data_points": len(data),
            "data": data
        }
    except Exception as e:
        print(f"Error in get_prices: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast", response_model=ForecastResponse)
async def create_forecast(
    request: ForecastRequest,
    current_user = Depends(get_current_user)
):
    """Generate LSTM price forecast (requires authentication)"""
    try:
        print(f"\n{'='*50}")
        print(f"Forecast for {request.commodity} by user {current_user.email}")
        print(f"{'='*50}\n")
        
        # Fetch data
        df = YahooFetcher.fetch_historical(request.commodity, period=request.period)
        prices = df['close'].tolist()
        dates = df['date'].tolist()
        
        print(f"Loaded {len(prices)} historical prices")
        
        # Train model
        forecaster = LSTMForecaster(
            window_size=request.window_size,
            forecast_horizon=request.forecast_days
        )
        
        print("\nTraining LSTM model...")
        train_metrics = forecaster.train(prices, epochs=50)
        print(f"Training completed in {train_metrics['training_time']:.2f}s")
        
        # Predict
        print(f"\nGenerating {request.forecast_days}-day forecast...")
        recent_prices = prices[-request.window_size:]
        predictions = forecaster.predict(recent_prices)
        
        # Future dates
        last_date = dates[-1]
        future_dates = []
        for i in range(1, request.forecast_days + 1):
            future_date = last_date + timedelta(days=i)
            future_dates.append(future_date.strftime('%Y-%m-%d'))
        
        # Format data
        historical_data = []
        display_count = min(100, len(prices))
        for i in range(len(prices) - display_count, len(prices)):
            historical_data.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'price': float(prices[i])
            })
        
        prediction_data = []
        for i, (date, price) in enumerate(zip(future_dates, predictions)):
            prediction_data.append({
                'date': date,
                'price': float(price),
                'day': i + 1
            })
        
        commodity_info = YahooFetcher.get_info(request.commodity)
        
        print(f"\nForecast completed!\n")
        
        return ForecastResponse(
            commodity=request.commodity,
            commodity_info=commodity_info,
            historical_data=historical_data,
            predictions=prediction_data,
            metrics={
                'training_loss': train_metrics['final_loss'],
                'training_time': train_metrics['training_time'],
                'data_points_used': len(prices)
            },
            model_info={
                'type': 'LSTM',
                'epochs': train_metrics['epochs']
            }
        )
        
    except Exception as e:
        print(f"\nError: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/forecast-compare")
async def compare_forecasts(
    request: ForecastRequest,
    current_user = Depends(get_current_user)
):
    """Generate forecasts using both LSTM and Transformer models"""
    try:
        print(f"\n{'='*50}")
        print(f"Comparison forecast for {request.commodity}")
        print(f"{'='*50}\n")
        
        # Fetch data
        df = YahooFetcher.fetch_historical(request.commodity, period=request.period)
        prices = df['close'].tolist()
        dates = df['date'].tolist()
        
        print(f"Loaded {len(prices)} historical prices")
        
        # Train LSTM
        print("\n--- Training LSTM ---")
        lstm_forecaster = LSTMForecaster(
            window_size=request.window_size,
            forecast_horizon=request.forecast_days
        )
        lstm_metrics = lstm_forecaster.train(prices, epochs=50)
        print(f"LSTM training completed in {lstm_metrics['training_time']:.2f}s")
        
        # Train Transformer
        print("\n--- Training Transformer ---")
        transformer_forecaster = TransformerForecaster(
            window_size=request.window_size,
            forecast_horizon=request.forecast_days
        )
        transformer_metrics = transformer_forecaster.train(prices, epochs=50)
        print(f"Transformer training completed in {transformer_metrics['training_time']:.2f}s")
        
        # Generate predictions
        print(f"\nGenerating predictions...")
        recent_prices = prices[-request.window_size:]
        
        lstm_predictions = lstm_forecaster.predict(recent_prices)
        transformer_predictions = transformer_forecaster.predict(recent_prices)
        
        # Future dates
        last_date = dates[-1]
        future_dates = []
        for i in range(1, request.forecast_days + 1):
            future_date = last_date + timedelta(days=i)
            future_dates.append(future_date.strftime('%Y-%m-%d'))
        
        # Format historical data
        historical_data = []
        display_count = min(100, len(prices))
        for i in range(len(prices) - display_count, len(prices)):
            historical_data.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'price': float(prices[i])
            })
        
        # Format predictions
        lstm_prediction_data = []
        transformer_prediction_data = []
        
        for i, (date, lstm_price, trans_price) in enumerate(zip(future_dates, lstm_predictions, transformer_predictions)):
            lstm_prediction_data.append({
                'date': date,
                'price': float(lstm_price),
                'day': i + 1
            })
            transformer_prediction_data.append({
                'date': date,
                'price': float(trans_price),
                'day': i + 1
            })
        
        commodity_info = YahooFetcher.get_info(request.commodity)
        
        print(f"\nComparison completed!\n")
        
        return {
            "commodity": request.commodity,
            "commodity_info": commodity_info,
            "historical_data": historical_data,
            "lstm_predictions": lstm_prediction_data,
            "transformer_predictions": transformer_prediction_data,
            "lstm_metrics": {
                'training_loss': lstm_metrics['final_loss'],
                'training_time': lstm_metrics['training_time'],
                'data_points_used': len(prices)
            },
            "transformer_metrics": {
                'training_loss': transformer_metrics['final_loss'],
                'training_time': transformer_metrics['training_time'],
                'data_points_used': len(prices)
            },
            "model_comparison": {
                'lstm_avg_price': float(np.mean(lstm_predictions)),
                'transformer_avg_price': float(np.mean(transformer_predictions)),
                'difference': float(abs(np.mean(lstm_predictions) - np.mean(transformer_predictions)))
            }
        }
        
    except Exception as e:
        print(f"\nError: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/{commodity}")
def get_commodity_news(commodity: str, limit: int = 10, force_refresh: bool = False):
    """Get news for specific commodity (with caching!)"""
    try:
        # Initialize cache
        cache = NewsCache(supabase)
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_articles = cache.get_cached_news(commodity)
            if cached_articles:
                return {
                    "commodity": commodity,
                    "articles": cached_articles[:limit],
                    "count": len(cached_articles[:limit]),
                    "source": "cache",
                    "cached": True
                }
        
        # Cache miss or force refresh - fetch from API
        print(f"Fetching fresh news for {commodity} from Alpha Vantage...")
        articles = AlphaVantageNewsFetcher.fetch_news(
            commodity=commodity,
            api_key=settings.alpha_vantage_api_key,
            limit=limit
        )
        
        # Cache the results
        if articles:
            cache.cache_news(commodity, articles, source='alpha_vantage')
        
        return {
            "commodity": commodity,
            "articles": articles,
            "count": len(articles),
            "source": "alpha_vantage",
            "cached": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news")
def get_general_news(limit: int = 20, force_refresh: bool = False):
    """Get general commodity market news (with caching!)"""
    try:
        # Use 'all' as the cache key for general news
        cache = NewsCache(supabase)
        
        # Try cache first
        if not force_refresh:
            cached_articles = cache.get_cached_news('all')
            if cached_articles:
                return {
                    "articles": cached_articles[:limit],
                    "count": len(cached_articles[:limit]),
                    "source": "cache",
                    "cached": True
                }
        
        # Fetch fresh
        print("Fetching fresh general news from Alpha Vantage...")
        articles = AlphaVantageNewsFetcher.fetch_general_news(
            api_key=settings.alpha_vantage_api_key,
            limit=limit
        )
        
        # Cache
        if articles:
            cache.cache_news('all', articles, source='alpha_vantage')
        
        return {
            "articles": articles,
            "count": len(articles),
            "source": "alpha_vantage",
            "cached": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/cache/stats")
def get_cache_stats():
    """Get cache statistics (admin endpoint)"""
    try:
        cache = NewsCache(supabase)
        stats = cache.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/cache/clear")
def clear_news_cache(commodity: Optional[str] = None):
    """Clear news cache (admin endpoint)"""
    try:
        cache = NewsCache(supabase)
        cache.clear_cache(commodity)
        return {"message": f"Cache cleared for {commodity if commodity else 'all commodities'}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio", response_model=List[PortfolioPositionResponse])
async def get_portfolio(user_id: str):
    """Get all portfolio positions for a user with current prices"""
    
    # Fetch positions from Supabase
    response = supabase.table("portfolio_positions")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    
    positions = response.data
    
    # Enrich each position with current price data
    enriched_positions = []
    
    for position in positions:
        # Get current price for the commodity
        current_price = None
        try:
            ticker = get_ticker_for_commodity(position['commodity'])
            if ticker:
                df = yf.download(ticker, period='1d', progress=False)
                if not df.empty:
                    current_price = float(df['Close'].iloc[-1])
        except Exception as e:
            print(f"Error fetching price for {position['commodity']}: {e}")
        
        # Calculate metrics
        quantity = float(position['quantity'])
        purchase_price = float(position['purchase_price'])
        purchase_value = quantity * purchase_price
        
        current_value = None
        profit_loss = None
        profit_loss_percent = None
        
        if current_price:
            current_value = quantity * current_price
            profit_loss = current_value - purchase_value
            profit_loss_percent = (profit_loss / purchase_value) * 100
        
        enriched_positions.append({
            **position,
            "current_price": current_price,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent
        })
    
    return enriched_positions

@app.post("/api/portfolio")
async def add_position(position: PortfolioPosition, user_id: str):
    """Add a new portfolio position"""
    
    data = {
        "user_id": user_id,
        "commodity": position.commodity,
        "quantity": position.quantity,
        "purchase_price": position.purchase_price,
        "purchase_date": position.purchase_date.isoformat(),
        "notes": position.notes
    }
    
    response = supabase.table("portfolio_positions").insert(data).execute()
    return {"message": "Position added successfully", "data": response.data}

@app.delete("/api/portfolio/{position_id}")
async def delete_position(position_id: str, user_id: str):
    """Delete a portfolio position"""

    response = supabase.table("portfolio_positions")\
        .delete()\
        .eq("id", position_id)\
        .eq("user_id", user_id)\
        .execute()

    return {"message": "Position deleted successfully"}


# Watchlist Endpoints

@app.get("/api/watchlist", response_model=List[WatchlistItemResponse])
async def get_watchlist(user_id: str):
    """Get user's watchlist commodities ordered by order_index"""

    response = supabase.table("watchlist_preferences")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("order_index")\
        .execute()

    return response.data

@app.post("/api/watchlist")
async def add_to_watchlist(item: WatchlistItem, user_id: str):
    """Add a commodity to user's watchlist"""

    # Get current max order_index for this user
    existing = supabase.table("watchlist_preferences")\
        .select("order_index")\
        .eq("user_id", user_id)\
        .order("order_index", desc=True)\
        .limit(1)\
        .execute()

    # Calculate next order_index
    next_order = 0
    if existing.data and len(existing.data) > 0:
        next_order = existing.data[0]["order_index"] + 1

    data = {
        "user_id": user_id,
        "commodity_id": item.commodity_id,
        "order_index": next_order
    }

    try:
        response = supabase.table("watchlist_preferences").insert(data).execute()
        return {"message": "Commodity added to watchlist", "data": response.data}
    except Exception as e:
        # Handle duplicate commodity error
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Commodity already in watchlist")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/watchlist/{commodity_id}")
async def remove_from_watchlist(commodity_id: str, user_id: str):
    """Remove a commodity from user's watchlist"""

    response = supabase.table("watchlist_preferences")\
        .delete()\
        .eq("commodity_id", commodity_id)\
        .eq("user_id", user_id)\
        .execute()

    return {"message": "Commodity removed from watchlist"}

@app.post("/api/watchlist/initialize")
async def initialize_watchlist(user_id: str):
    """Initialize default watchlist for new user (Gold, Silver, Crude Oil)"""

    # Check if user already has watchlist items
    existing = supabase.table("watchlist_preferences")\
        .select("id")\
        .eq("user_id", user_id)\
        .execute()

    if existing.data and len(existing.data) > 0:
        return {"message": "Watchlist already initialized", "items": existing.data}

    # Insert default items
    default_items = [
        {"user_id": user_id, "commodity_id": "gold", "order_index": 0},
        {"user_id": user_id, "commodity_id": "silver", "order_index": 1},
        {"user_id": user_id, "commodity_id": "crude_oil", "order_index": 2}
    ]

    response = supabase.table("watchlist_preferences").insert(default_items).execute()
    return {"message": "Default watchlist initialized", "data": response.data}