"""Forecasting endpoints"""

from fastapi import APIRouter, HTTPException, Depends

from app.schemas.forecast import (
    ForecastRequest, 
    ForecastResponse, 
    ForecastComparisonResponse
)
from app.api.v1.deps import get_current_user
from app.services.forecast_service import ForecastService
from app.data.fetchers.yahoo_fetcher import YahooFetcher

router = APIRouter()


@router.post("/api/forecast", response_model=ForecastResponse)
async def create_forecast(
    request: ForecastRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate LSTM price forecast for a commodity.
    
    Requires authentication. Trains an LSTM neural network on historical price data
    and generates multi-day price predictions.
    
    Args:
        request: Forecast parameters (commodity, forecast_days, window_size, period)
        current_user: Authenticated user (injected by dependency)
        
    Returns:
        Historical data, predictions, training metrics, and model info
        
    Raises:
        HTTPException: 500 if forecasting fails
    """
    try:
        print(f"\n{'='*50}")
        print(f"Forecast for {request.commodity} by user {current_user.email}")
        print(f"{'='*50}\n")
        
        # Fetch historical data
        prices, dates = ForecastService.fetch_historical_data(
            request.commodity, 
            request.period
        )
        print(f"Loaded {len(prices)} historical prices")
        
        # Train LSTM model
        forecaster, train_metrics = ForecastService.train_lstm_model(
            prices, 
            request.window_size, 
            request.forecast_days,
            epochs=50
        )
        
        # Generate predictions
        print(f"\nGenerating {request.forecast_days}-day forecast...")
        recent_prices = prices[-request.window_size:]
        predictions = forecaster.predict(recent_prices)
        
        # Generate future dates
        last_date = dates[-1]
        future_dates = ForecastService.generate_future_dates(last_date, request.forecast_days)
        
        # Format response data
        historical_data = ForecastService.format_historical_data(prices, dates, display_count=100)
        prediction_data = ForecastService.format_predictions(predictions, future_dates)
        
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
        raise HTTPException(
            status_code=500, 
            detail=f"Forecast generation failed: {str(e)}"
        )


@router.post("/api/forecast-compare", response_model=ForecastComparisonResponse)
async def compare_forecasts(
    request: ForecastRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate and compare forecasts using both LSTM and Transformer models.
    
    Requires authentication. Trains both models on the same data and returns
    side-by-side predictions for comparison.
    
    Args:
        request: Forecast parameters
        current_user: Authenticated user (injected by dependency)
        
    Returns:
        Historical data, predictions from both models, metrics, and comparison stats
        
    Raises:
        HTTPException: 500 if forecasting fails
    """
    try:
        print(f"\n{'='*50}")
        print(f"Comparison forecast for {request.commodity}")
        print(f"{'='*50}\n")
        
        # Fetch historical data
        prices, dates = ForecastService.fetch_historical_data(
            request.commodity, 
            request.period
        )
        print(f"Loaded {len(prices)} historical prices")
        
        # Train both models
        print("\n--- Training LSTM ---")
        lstm_forecaster, lstm_metrics = ForecastService.train_lstm_model(
            prices, 
            request.window_size, 
            request.forecast_days,
            epochs=50
        )
        
        print("\n--- Training Transformer ---")
        transformer_forecaster, transformer_metrics = ForecastService.train_transformer_model(
            prices, 
            request.window_size, 
            request.forecast_days,
            epochs=50
        )
        
        # Generate predictions
        print(f"\nGenerating predictions...")
        recent_prices = prices[-request.window_size:]
        
        lstm_predictions = lstm_forecaster.predict(recent_prices)
        transformer_predictions = transformer_forecaster.predict(recent_prices)
        
        # Generate future dates
        last_date = dates[-1]
        future_dates = ForecastService.generate_future_dates(last_date, request.forecast_days)
        
        # Format response data
        historical_data = ForecastService.format_historical_data(prices, dates, display_count=100)
        lstm_prediction_data = ForecastService.format_predictions(lstm_predictions, future_dates)
        transformer_prediction_data = ForecastService.format_predictions(transformer_predictions, future_dates)
        
        # Calculate comparison metrics
        comparison = ForecastService.calculate_comparison_metrics(
            lstm_predictions,
            transformer_predictions
        )
        
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
            "model_comparison": comparison
        }
        
    except Exception as e:
        print(f"\nError: {str(e)}\n")
        raise HTTPException(
            status_code=500, 
            detail=f"Forecast comparison failed: {str(e)}"
        )
