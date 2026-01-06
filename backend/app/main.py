from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from datetime import timedelta
from supabase import create_client
import pandas as pd

from app.data.fetchers.yahoo_fetcher import YahooFetcher
from app.models.lstm_forecaster import LSTMForecaster
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