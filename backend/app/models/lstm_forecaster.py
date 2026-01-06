import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List
import time

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class LSTMForecaster:
    def __init__(self, window_size=60, forecast_horizon=30, hidden_size=50, num_layers=2):
        self.window_size = window_size
        self.forecast_horizon = forecast_horizon
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def prepare_data(self, prices: List[float]) -> Tuple[torch.Tensor, torch.Tensor]:
        prices_array = np.array(prices).reshape(-1, 1)
        scaled_prices = self.scaler.fit_transform(prices_array)
        
        X, y = [], []
        for i in range(len(scaled_prices) - self.window_size):
            X.append(scaled_prices[i:i + self.window_size])
            y.append(scaled_prices[i + self.window_size])
        
        X = torch.FloatTensor(np.array(X)).to(self.device)
        y = torch.FloatTensor(np.array(y)).to(self.device)
        return X, y
    
    def train(self, prices: List[float], epochs=50, lr=0.001, batch_size=32) -> dict:
        start_time = time.time()
        X, y = self.prepare_data(prices)
        
        self.model = LSTMModel(
            input_size=1,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        ).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        self.model.train()
        losses = []
        
        for epoch in range(epochs):
            epoch_loss = 0
            num_batches = 0
            
            for i in range(0, len(X), batch_size):
                batch_X = X[i:i+batch_size]
                batch_y = y[i:i+batch_size]
                
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_loss = epoch_loss / num_batches
            losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.6f}')
        
        training_time = time.time() - start_time
        return {
            'final_loss': losses[-1],
            'training_time': training_time,
            'epochs': epochs
        }
    
    def predict(self, recent_prices: List[float], num_steps=None) -> List[float]:
        if num_steps is None:
            num_steps = self.forecast_horizon
        
        self.model.eval()
        
        if len(recent_prices) < self.window_size:
            raise ValueError(f"Need at least {self.window_size} recent prices")
        
        input_prices = recent_prices[-self.window_size:]
        input_prices = np.array(input_prices).reshape(-1, 1)
        scaled_input = self.scaler.transform(input_prices)
        
        predictions = []
        current_input = torch.FloatTensor(scaled_input).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            for _ in range(num_steps):
                pred = self.model(current_input)
                predictions.append(pred.item())
                new_input = torch.cat([current_input[:, 1:, :], pred.unsqueeze(1)], dim=1)
                current_input = new_input
        
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        return predictions.flatten().tolist()