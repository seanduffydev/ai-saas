"""Forecasting schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ForecastRequest(BaseModel):
    """Request body for forecast generation"""
    commodity: str = Field(..., description="Commodity name (e.g., 'Gold', 'Silver')")
    forecast_days: int = Field(30, ge=1, le=365, description="Number of days to forecast")
    window_size: int = Field(60, ge=10, le=365, description="Historical window size for training")
    period: str = Field('2y', description="Historical data period (e.g., '1y', '2y', '5y')")


class HistoricalDataPoint(BaseModel):
    """Historical price data point"""
    date: str
    price: float


class PredictionDataPoint(BaseModel):
    """Predicted price data point"""
    date: str
    price: float
    day: int


class ModelMetrics(BaseModel):
    """Model training metrics"""
    training_loss: float
    training_time: float
    data_points_used: int


class ModelInfo(BaseModel):
    """Model information"""
    type: str
    epochs: int


class ForecastResponse(BaseModel):
    """Forecast generation response"""
    commodity: str
    commodity_info: Dict[str, Any]
    historical_data: List[HistoricalDataPoint]
    predictions: List[PredictionDataPoint]
    metrics: ModelMetrics
    model_info: ModelInfo


class ComparisonMetrics(BaseModel):
    """Model comparison metrics"""
    lstm_avg_price: float
    transformer_avg_price: float
    difference: float


class ForecastComparisonResponse(BaseModel):
    """Forecast comparison response for multiple models"""
    commodity: str
    commodity_info: Dict[str, Any]
    historical_data: List[HistoricalDataPoint]
    lstm_predictions: List[PredictionDataPoint]
    transformer_predictions: List[PredictionDataPoint]
    lstm_metrics: ModelMetrics
    transformer_metrics: ModelMetrics
    model_comparison: ComparisonMetrics
