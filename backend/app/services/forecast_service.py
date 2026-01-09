"""Forecasting business logic"""

from typing import List, Tuple
from datetime import timedelta
import numpy as np

from app.models.lstm_forecaster import LSTMForecaster
from app.models.transformer_forecaster import TransformerForecaster
from app.data.fetchers.yahoo_fetcher import YahooFetcher


class ForecastService:
    """Service for handling forecast operations"""
    
    @staticmethod
    def fetch_historical_data(commodity: str, period: str) -> Tuple[List[float], List]:
        """
        Fetch historical price data for a commodity.
        
        Args:
            commodity: Commodity name
            period: Time period (e.g., '1y', '2y')
            
        Returns:
            Tuple of (prices, dates)
        """
        df = YahooFetcher.fetch_historical(commodity, period=period)
        prices = df['close'].tolist()
        dates = df['date'].tolist()
        return prices, dates
    
    @staticmethod
    def train_lstm_model(
        prices: List[float], 
        window_size: int, 
        forecast_days: int,
        epochs: int = 50
    ) -> Tuple[LSTMForecaster, dict]:
        """
        Train LSTM forecasting model.
        
        Args:
            prices: Historical price data
            window_size: Size of input window
            forecast_days: Number of days to forecast
            epochs: Training epochs
            
        Returns:
            Tuple of (trained_model, training_metrics)
        """
        print("\nTraining LSTM model...")
        forecaster = LSTMForecaster(
            window_size=window_size,
            forecast_horizon=forecast_days
        )
        metrics = forecaster.train(prices, epochs=epochs)
        print(f"Training completed in {metrics['training_time']:.2f}s")
        return forecaster, metrics
    
    @staticmethod
    def train_transformer_model(
        prices: List[float], 
        window_size: int, 
        forecast_days: int,
        epochs: int = 50
    ) -> Tuple[TransformerForecaster, dict]:
        """
        Train Transformer forecasting model.
        
        Args:
            prices: Historical price data
            window_size: Size of input window
            forecast_days: Number of days to forecast
            epochs: Training epochs
            
        Returns:
            Tuple of (trained_model, training_metrics)
        """
        print("\nTraining Transformer model...")
        forecaster = TransformerForecaster(
            window_size=window_size,
            forecast_horizon=forecast_days
        )
        metrics = forecaster.train(prices, epochs=epochs)
        print(f"Training completed in {metrics['training_time']:.2f}s")
        return forecaster, metrics
    
    @staticmethod
    def generate_future_dates(last_date, forecast_days: int) -> List[str]:
        """
        Generate list of future dates for predictions.
        
        Args:
            last_date: Last historical date
            forecast_days: Number of future days
            
        Returns:
            List of date strings in YYYY-MM-DD format
        """
        future_dates = []
        for i in range(1, forecast_days + 1):
            future_date = last_date + timedelta(days=i)
            future_dates.append(future_date.strftime('%Y-%m-%d'))
        return future_dates
    
    @staticmethod
    def format_historical_data(prices: List[float], dates: List, display_count: int = 100) -> List[dict]:
        """
        Format historical data for API response.
        
        Args:
            prices: Price values
            dates: Date values
            display_count: Number of recent points to include
            
        Returns:
            List of formatted data points
        """
        historical_data = []
        count = min(display_count, len(prices))
        for i in range(len(prices) - count, len(prices)):
            historical_data.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'price': float(prices[i])
            })
        return historical_data
    
    @staticmethod
    def format_predictions(predictions: List[float], dates: List[str]) -> List[dict]:
        """
        Format prediction data for API response.
        
        Args:
            predictions: Predicted price values
            dates: Future date strings
            
        Returns:
            List of formatted prediction points
        """
        prediction_data = []
        for i, (date, price) in enumerate(zip(dates, predictions)):
            prediction_data.append({
                'date': date,
                'price': float(price),
                'day': i + 1
            })
        return prediction_data
    
    @staticmethod
    def calculate_comparison_metrics(
        lstm_predictions: List[float],
        transformer_predictions: List[float]
    ) -> dict:
        """
        Calculate comparison metrics between two models.
        
        Args:
            lstm_predictions: LSTM model predictions
            transformer_predictions: Transformer model predictions
            
        Returns:
            Dictionary with comparison metrics
        """
        return {
            'lstm_avg_price': float(np.mean(lstm_predictions)),
            'transformer_avg_price': float(np.mean(transformer_predictions)),
            'difference': float(abs(np.mean(lstm_predictions) - np.mean(transformer_predictions)))
        }
