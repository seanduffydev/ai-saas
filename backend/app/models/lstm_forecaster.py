"""LSTM-based time series forecaster for commodity prices."""

import time

import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler


class LSTMModel(nn.Module):
    """PyTorch LSTM module for sequence-to-one price prediction."""

    def __init__(self, input_size=1, hidden_size=50, num_layers=2, dropout=0.2):
        """Initialize the LSTM model.

        Args:
            input_size: Number of input features per timestep (default 1 for price).
            hidden_size: LSTM hidden state size.
            num_layers: Number of stacked LSTM layers.
            dropout: Dropout probability (applied between layers if num_layers > 1).
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        """Forward pass: map input sequence to single-step prediction.

        Args:
            x: Input tensor of shape (batch_size, seq_len, input_size).

        Returns:
            Tensor of shape (batch_size, 1) with predicted value.
        """
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


class LSTMForecaster:
    """LSTM-based forecaster for commodity price time series.

    Trains on historical prices and produces multi-step ahead predictions
    using a MinMax-scaled LSTM with configurable window and horizon.
    """

    def __init__(
        self, window_size=60, forecast_horizon=30, hidden_size=50, num_layers=2
    ):
        """Initialize the forecaster.

        Args:
            window_size: Number of past prices used as input (sequence length).
            forecast_horizon: Default number of steps to predict ahead.
            hidden_size: LSTM hidden size.
            num_layers: Number of LSTM layers.
        """
        self.window_size = window_size
        self.forecast_horizon = forecast_horizon
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def prepare_data(self, prices: list[float]) -> tuple[torch.Tensor, torch.Tensor]:
        """Build supervised (X, y) sequences from a price series.

        Args:
            prices: List of historical closing prices.

        Returns:
            Tuple of (X, y) tensors on self.device. X has shape
            (n_samples, window_size, 1), y has shape (n_samples, 1).
        """
        prices_array = np.array(prices).reshape(-1, 1)
        scaled_prices = self.scaler.fit_transform(prices_array)

        X, y = [], []
        for i in range(len(scaled_prices) - self.window_size):
            X.append(scaled_prices[i : i + self.window_size])
            y.append(scaled_prices[i + self.window_size])

        X = torch.FloatTensor(np.array(X)).to(self.device)
        y = torch.FloatTensor(np.array(y)).to(self.device)
        return X, y

    def train(self, prices: list[float], epochs=50, lr=0.001, batch_size=32) -> dict:
        """Train the LSTM on historical prices.

        Args:
            prices: Historical price series.
            epochs: Number of training epochs.
            lr: Learning rate for Adam optimizer.
            batch_size: Mini-batch size for training.

        Returns:
            Dict with 'final_loss', 'training_time', and 'epochs'.
        """
        start_time = time.time()

        if len(prices) <= self.window_size:
            raise ValueError(
                f"Need more than {self.window_size} prices to train; got {len(prices)}"
            )

        X, y = self.prepare_data(prices)

        self.model = LSTMModel(
            input_size=1, hidden_size=self.hidden_size, num_layers=self.num_layers
        ).to(self.device)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        self.model.train()
        losses = []

        for epoch in range(epochs):
            epoch_loss = 0
            num_batches = 0

            for i in range(0, len(X), batch_size):
                batch_X = X[i : i + batch_size]
                batch_y = y[i : i + batch_size]

                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1

            num_batches = max(num_batches, 1)
            avg_loss = epoch_loss / num_batches
            losses.append(avg_loss)

            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch + 1}/{epochs}], Loss: {avg_loss:.6f}")

        training_time = time.time() - start_time
        return {
            "final_loss": losses[-1],
            "training_time": training_time,
            "epochs": epochs,
        }

    def predict(self, recent_prices: list[float], num_steps=None) -> list[float]:
        """Produce multi-step ahead price predictions.

        Args:
            recent_prices: Most recent prices (length must be >= window_size).
            num_steps: Number of steps to predict; defaults to forecast_horizon.

        Returns:
            List of predicted prices (length num_steps) in original scale.

        Raises:
            ValueError: If len(recent_prices) < window_size.
        """
        if num_steps is None:
            num_steps = self.forecast_horizon

        if self.model is None:
            raise ValueError("Model has not been trained. Call train() first.")

        self.model.eval()

        if len(recent_prices) < self.window_size:
            raise ValueError(f"Need at least {self.window_size} recent prices")

        input_prices = recent_prices[-self.window_size :]
        input_prices = np.array(input_prices).reshape(-1, 1)
        scaled_input = self.scaler.transform(input_prices)

        predictions = []
        current_input = torch.FloatTensor(scaled_input).unsqueeze(0).to(self.device)

        with torch.no_grad():
            for _ in range(num_steps):
                pred = self.model(current_input)
                predictions.append(pred.item())
                new_input = torch.cat(
                    [current_input[:, 1:, :], pred.unsqueeze(1)], dim=1
                )
                current_input = new_input

        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        return predictions.flatten().tolist()
