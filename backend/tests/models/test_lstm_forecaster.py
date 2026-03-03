"""Tests for LSTM forecaster model."""

import pytest

from app.models.lstm_forecaster import LSTMForecaster


def test_prepare_data():
    """prepare_data returns X, y with correct shapes."""
    forecaster = LSTMForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i for i in range(20)]
    X, y = forecaster.prepare_data(prices)
    assert X.shape[0] == 15  # 20 - 5
    assert X.shape[1] == 5
    assert X.shape[2] == 1
    assert y.shape[0] == 15
    assert y.shape[1] == 1


def test_train_returns_metrics():
    """train() returns dict with final_loss, training_time, epochs."""
    forecaster = LSTMForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i * 0.5 for i in range(25)]
    metrics = forecaster.train(prices, epochs=2, batch_size=8)
    assert "final_loss" in metrics
    assert "training_time" in metrics
    assert metrics["epochs"] == 2
    assert forecaster.model is not None


def test_predict_returns_list():
    """predict() returns list of length forecast_horizon."""
    forecaster = LSTMForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0 + i * 0.5 for i in range(25)]
    forecaster.train(prices, epochs=2)
    recent = prices[-5:]
    preds = forecaster.predict(recent, num_steps=3)
    assert len(preds) == 3
    assert all(isinstance(p, (int, float)) for p in preds)


def test_predict_insufficient_prices_raises():
    """predict() with fewer than window_size prices raises ValueError."""
    forecaster = LSTMForecaster(window_size=5, forecast_horizon=3)
    prices = [100.0, 101.0]  # only 2
    with pytest.raises(ValueError, match="Need at least 5 recent prices"):
        forecaster.predict(prices)


def test_predict_uses_num_steps():
    """predict() with num_steps returns that many values."""
    forecaster = LSTMForecaster(window_size=5, forecast_horizon=30)
    prices = [100.0 + i for i in range(20)]
    forecaster.train(prices, epochs=2)
    preds = forecaster.predict(prices[-5:], num_steps=7)
    assert len(preds) == 7
