"""Tests for forecast schemas."""

import pytest
from datetime import date
from app.schemas.forecast import (
    ForecastRequest,
    ForecastResponse,
    HistoricalDataPoint,
    PredictionDataPoint,
    ModelMetrics,
    ModelInfo,
    ComparisonMetrics,
    ForecastComparisonResponse,
)


def test_forecast_request_valid():
    r = ForecastRequest(commodity="gold", forecast_days=30, window_size=60, period="2y")
    assert r.commodity == "gold"
    assert r.forecast_days == 30
    assert r.window_size == 60
    assert r.period == "2y"


def test_forecast_request_defaults():
    r = ForecastRequest(commodity="silver")
    assert r.forecast_days == 30
    assert r.window_size == 60
    assert r.period == "2y"


def test_forecast_request_validation_forecast_days():
    with pytest.raises(ValueError):
        ForecastRequest(commodity="gold", forecast_days=0)
    with pytest.raises(ValueError):
        ForecastRequest(commodity="gold", forecast_days=400)


def test_historical_data_point():
    p = HistoricalDataPoint(date="2024-01-01", price=100.5)
    assert p.date == "2024-01-01"
    assert p.price == 100.5


def test_prediction_data_point():
    p = PredictionDataPoint(date="2024-02-01", price=105.0, day=1)
    assert p.day == 1


def test_forecast_response():
    r = ForecastResponse(
        commodity="gold",
        commodity_info={"name": "Gold", "category": "Metals"},
        historical_data=[HistoricalDataPoint(date="2024-01-01", price=100.0)],
        predictions=[PredictionDataPoint(date="2024-02-01", price=102.0, day=1)],
        metrics=ModelMetrics(training_loss=0.01, training_time=1.5, data_points_used=100),
        model_info=ModelInfo(type="LSTM", epochs=50),
    )
    assert r.commodity == "gold"
    assert len(r.historical_data) == 1
    assert r.model_info.epochs == 50


def test_comparison_metrics():
    c = ComparisonMetrics(lstm_avg_price=100.0, transformer_avg_price=101.0, difference=1.0)
    assert c.difference == 1.0
