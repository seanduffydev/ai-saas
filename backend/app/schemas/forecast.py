"""Pydantic schemas for forecast API requests and responses."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Request body for forecast generation.

    Attributes:
        commodity: Commodity name (e.g., 'Gold', 'Silver').
        forecast_days: Number of days to forecast (1-365).
        window_size: Historical window size for training (10-365).
        period: Historical data period (e.g., '1y', '2y', '5y').
    """

    commodity: str = Field(..., description="Commodity name (e.g., 'Gold', 'Silver')")
    forecast_days: int = Field(30, ge=1, le=365, description="Number of days to forecast")
    window_size: int = Field(60, ge=10, le=365, description="Historical window size for training")
    period: str = Field('2y', description="Historical data period (e.g., '1y', '2y', '5y')")


class HistoricalDataPoint(BaseModel):
    """Single historical price data point.

    Attributes:
        date: Date string (YYYY-MM-DD).
        price: Closing price.
    """

    date: str
    price: float


class PredictionDataPoint(BaseModel):
    """Single predicted price data point.

    Attributes:
        date: Forecast date string.
        price: Predicted price.
        day: One-based day index in forecast horizon.
    """

    date: str
    price: float
    day: int


class ModelMetrics(BaseModel):
    """Model training metrics.

    Attributes:
        training_loss: Final epoch loss.
        training_time: Training duration in seconds.
        data_points_used: Number of historical points used.
    """

    training_loss: float
    training_time: float
    data_points_used: int


class ModelInfo(BaseModel):
    """Model metadata.

    Attributes:
        type: Model type (e.g. 'LSTM', 'Transformer').
        epochs: Number of training epochs.
    """

    type: str
    epochs: int


class ForecastResponse(BaseModel):
    """Full forecast API response.

    Attributes:
        commodity: Commodity name.
        commodity_info: Metadata dict for the commodity.
        historical_data: Recent historical price points.
        predictions: Forecast data points.
        metrics: Training metrics.
        model_info: Model metadata.
    """

    commodity: str
    commodity_info: Dict[str, Any]
    historical_data: List[HistoricalDataPoint]
    predictions: List[PredictionDataPoint]
    metrics: ModelMetrics
    model_info: ModelInfo


class ComparisonMetrics(BaseModel):
    """Comparison metrics between LSTM and Transformer forecasts.

    Attributes:
        lstm_avg_price: Mean of LSTM predictions.
        transformer_avg_price: Mean of Transformer predictions.
        difference: Absolute difference of the two means.
    """

    lstm_avg_price: float
    transformer_avg_price: float
    difference: float


class ForecastComparisonResponse(BaseModel):
    """Response when comparing LSTM and Transformer forecasts.

    Attributes:
        commodity: Commodity name.
        commodity_info: Commodity metadata.
        historical_data: Historical price points.
        lstm_predictions: LSTM forecast points.
        transformer_predictions: Transformer forecast points.
        lstm_metrics: LSTM training metrics.
        transformer_metrics: Transformer training metrics.
        model_comparison: Comparison metrics.
    """

    commodity: str
    commodity_info: Dict[str, Any]
    historical_data: List[HistoricalDataPoint]
    lstm_predictions: List[PredictionDataPoint]
    transformer_predictions: List[PredictionDataPoint]
    lstm_metrics: ModelMetrics
    transformer_metrics: ModelMetrics
    model_comparison: ComparisonMetrics
