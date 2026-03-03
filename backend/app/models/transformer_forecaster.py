"""Transformer-based time series forecaster for commodity prices."""

import math
import time

import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for Transformer sequences."""

    def __init__(self, d_model, max_len=5000):
        """Initialize positional encoding matrix.

        Args:
            d_model: Embedding dimension.
            max_len: Maximum sequence length to support.
        """
        super().__init__()

        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x):
        """Add positional encoding to input.

        Args:
            x: Input tensor (batch, seq_len, d_model).

        Returns:
            Tensor of same shape as x with positional encoding added.
        """
        return x + self.pe[:, : x.size(1), :]


class TransformerModel(nn.Module):
    """Transformer encoder for sequence-to-one time series prediction."""

    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2, dropout=0.1):
        """Initialize the Transformer model.

        Args:
            input_size: Input feature size per timestep (e.g. 1 for price).
            d_model: Transformer embedding dimension.
            nhead: Number of attention heads.
            num_layers: Number of encoder layers.
            dropout: Dropout probability.
        """
        super().__init__()
        self.d_model = d_model

        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)

        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model)

        # Transformer encoder
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)

        # Output projection
        self.fc = nn.Linear(d_model, 1)

    def forward(self, x):
        """Forward pass: sequence to single-step prediction.

        Args:
            x: Input tensor (batch, seq_len, input_size).

        Returns:
            Tensor (batch, 1) with predicted value.
        """
        # x shape: (batch, seq_len, input_size)

        # Project input to d_model dimensions
        x = self.input_projection(x)  # (batch, seq_len, d_model)

        # Add positional encoding
        x = self.pos_encoder(x)

        # Pass through transformer
        x = self.transformer_encoder(x)  # (batch, seq_len, d_model)

        # Use last timestep for prediction
        x = x[:, -1, :]  # (batch, d_model)

        # Project to output
        out = self.fc(x)  # (batch, 1)

        return out


class TransformerForecaster:
    """Transformer-based forecaster for commodity price time series."""

    def __init__(
        self, window_size=60, forecast_horizon=30, d_model=64, nhead=4, num_layers=2
    ):
        """Initialize the forecaster.

        Args:
            window_size: Input sequence length (number of past prices).
            forecast_horizon: Default number of steps to predict.
            d_model: Transformer embedding dimension.
            nhead: Number of attention heads.
            num_layers: Number of encoder layers.
        """
        self.window_size = window_size
        self.forecast_horizon = forecast_horizon
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def prepare_data(self, prices: list[float]) -> tuple[torch.Tensor, torch.Tensor]:
        """Build (X, y) sequences from price series.

        Args:
            prices: List of historical closing prices.

        Returns:
            Tuple of (X, y) tensors. X: (n_samples, window_size, 1), y: (n_samples, 1).
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
        """Train the Transformer on historical prices.

        Args:
            prices: Historical price series.
            epochs: Number of training epochs.
            lr: Learning rate for Adam.
            batch_size: Mini-batch size.

        Returns:
            Dict with 'final_loss', 'training_time', and 'epochs'.
        """
        start_time = time.time()

        if len(prices) <= self.window_size:
            raise ValueError(
                f"Need more than {self.window_size} prices to train; got {len(prices)}"
            )

        X, y = self.prepare_data(prices)

        self.model = TransformerModel(
            input_size=1,
            d_model=self.d_model,
            nhead=self.nhead,
            num_layers=self.num_layers,
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
            recent_prices: Most recent prices (length >= window_size).
            num_steps: Number of steps to predict; defaults to forecast_horizon.

        Returns:
            List of predicted prices in original scale.

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
