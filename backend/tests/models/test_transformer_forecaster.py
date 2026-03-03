"""Tests for Transformer forecaster model."""

import pytest

from app.models.transformer_forecaster import TransformerForecaster


def test_prepare_data():
    """prepare_data returns X, y with correct shapes."""
    forecaster = TransformerForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i for i in range(20)]
    X, y = forecaster.prepare_data(prices)
    assert X.shape[0] == 15
    assert X.shape[1] == 5
    assert X.shape[2] == 1
    assert y.shape[0] == 15


def test_train_returns_metrics():
    """train() returns dict with final_loss, training_time, epochs."""
    forecaster = TransformerForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i * 0.5 for i in range(25)]
    metrics = forecaster.train(prices, epochs=2, batch_size=8)
    assert "final_loss" in metrics
    assert "training_time" in metrics
    assert metrics["epochs"] == 2
    assert forecaster.model is not None


def test_predict_returns_list():
    """predict() returns list of length forecast_horizon."""
    forecaster = TransformerForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i * 0.5 for i in range(25)]
    forecaster.train(prices, epochs=2)
    recent = prices[-5:]
    preds = forecaster.predict(recent, num_steps=3)
    assert len(preds) == 3
    assert all(isinstance(p, (int, float)) for p in preds)


def test_predict_insufficient_prices_raises():
    """predict() with fewer than window_size prices raises ValueError."""
    forecaster = TransformerForecaster(window_size=5, forecast_horizon=3)
    train_prices = [100.0 + i for i in range(20)]
    forecaster.train(train_prices, epochs=1)
    with pytest.raises(ValueError, match="Need at least 5 recent prices"):
        forecaster.predict([100.0, 101.0])
