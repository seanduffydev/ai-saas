import { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import axios from 'axios';
import './App.css';

import CommoditySelector from './components/CommoditySelector';
import ForecastChart from './components/ForecastChart';
import MetricsDisplay from './components/MetricsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ComparisonChart from './components/ComparisonChart';
import ComparisonMetrics from './components/ComparisonMetrics';

function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);

  // Commodity forecasting state
  const [commodities, setCommodities] = useState([]);
  const [selectedCommodity, setSelectedCommodity] = useState('');
  const [forecastDays, setForecastDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [forecastData, setForecastData] = useState(null);
  const [error, setError] = useState(null);
  const [modelMode, setModelMode] = useState('single');
  const [selectedModel, setSelectedModel] = useState('lstm');
  const [comparisonData, setComparisonData] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Check authentication
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Load commodities when user logs in
  // Load commodities when user logs in
  useEffect(() => {
    if (user) {
      loadCommodities();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const loadCommodities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/commodities`);
      setCommodities(response.data.commodities);
    } catch (error) {
      console.error('Error loading commodities:', error);
      setError('Failed to load commodities');
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError(null);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setError(error.message);
    } else {
      alert('Check your email for confirmation!');
    }
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setForecastData(null);
    setSelectedCommodity('');
  };

  const handleGenerateForecast = async () => {
    if (!selectedCommodity) {
      setError('Please select a commodity');
      return;
    }

    setLoading(true);
    setError(null);
    setForecastData(null);
    setComparisonData(null);
    setLoadingMessage('Fetching historical data...');

    try {
      const session = await supabase.auth.getSession();
      const token = session.data.session?.access_token;

      setLoadingMessage(`Training ${selectedModel.toUpperCase()} model...`);

      const response = await axios.post(
        `${API_URL}/api/forecast`,
        {
          commodity: selectedCommodity,
          forecast_days: forecastDays,
          window_size: 60,
          period: '2y'
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setLoadingMessage('Generating predictions...');
      setForecastData(response.data);

    } catch (error) {
      console.error('Error generating forecast:', error);
      setError(error.response?.data?.detail || 'Failed to generate forecast');
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleCompareModels = async () => {
    if (!selectedCommodity) {
      setError('Please select a commodity');
      return;
    }

    setLoading(true);
    setError(null);
    setForecastData(null);
    setComparisonData(null);
    setLoadingMessage('Fetching historical data...');

    try {
      const session = await supabase.auth.getSession();
      const token = session.data.session?.access_token;

      setLoadingMessage('Training both LSTM and Transformer models...');
      setLoadingMessage('This may take 1-2 minutes...');

      const response = await axios.post(
        `${API_URL}/api/forecast-compare`,
        {
          commodity: selectedCommodity,
          forecast_days: forecastDays,
          window_size: 60,
          period: '2y'
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setLoadingMessage('Generating comparison...');
      setComparisonData(response.data);

    } catch (error) {
      console.error('Error comparing models:', error);
      setError(error.response?.data?.detail || 'Failed to compare models');
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  };

  // Login/Signup UI
  if (!user) {
    return (
      <div className="App">
        <div className="auth-container">
          <h1>📈 Commodity Forecasting Lab</h1>
          <p className="subtitle">AI-Powered LSTM Price Predictions</p>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={isSignUp ? handleSignUp : handleSignIn}>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password (min 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit" className="primary-button">
              {isSignUp ? 'Sign Up' : 'Sign In'}
            </button>
          </form>

          <div className="auth-toggle">
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}
            {' '}
            <button onClick={() => setIsSignUp(!isSignUp)} className="link-button">
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main forecasting UI
  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>📈 Commodity Forecasting Lab</h1>
          <div className="user-info">
            <span>{user.email}</span>
            <button onClick={handleSignOut} className="sign-out-button">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {error && <div className="error-message">{error}</div>}

        <div className="controls-section">
          <CommoditySelector
            commodities={commodities}
            selectedCommodity={selectedCommodity}
            onSelect={setSelectedCommodity}
            disabled={loading}
          />

          <div className="forecast-controls">
            <label htmlFor="forecast-days">Forecast Horizon:</label>
            <select
              id="forecast-days"
              value={forecastDays}
              onChange={(e) => setForecastDays(Number(e.target.value))}
              disabled={loading}
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>

          <div className="forecast-controls">
            <label htmlFor="model-mode">Prediction Mode:</label>
            <select
              id="model-mode"
              value={modelMode}
              onChange={(e) => {
                setModelMode(e.target.value);
                setForecastData(null);
                setComparisonData(null);
              }}
              disabled={loading}
            >
              <option value="single">Single Model</option>
              <option value="compare">Compare Models</option>
            </select>
          </div>

          {modelMode === 'single' && (
            <div className="forecast-controls">
              <label htmlFor="model-select">AI Model:</label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={loading}
              >
                <option value="lstm">LSTM</option>
                <option value="transformer">Transformer</option>
              </select>
            </div>
          )}

          <button
            onClick={modelMode === 'compare' ? handleCompareModels : handleGenerateForecast}
            disabled={!selectedCommodity || loading}
            className="generate-button"
          >
            {loading ? '⏳ Generating...' :
              modelMode === 'compare' ? '⚡ Compare Models' : '🚀 Generate Forecast'}
          </button>
        </div>

        {loading && <LoadingSpinner message={loadingMessage} />}

        {/* Single Model Results */}
        {forecastData && !loading && !comparisonData && (
          <div className="results-section">
            <ForecastChart
              historicalData={forecastData.historical_data}
              predictions={forecastData.predictions}
              commodityInfo={forecastData.commodity_info}
            />

            <MetricsDisplay
              metrics={forecastData.metrics}
              modelInfo={forecastData.model_info}
              predictions={forecastData.predictions}
            />

            <div className="predictions-table">
              <h3>📋 Predicted Prices</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Day</th>
                      <th>Date</th>
                      <th>Predicted Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecastData.predictions.slice(0, 10).map((pred, idx) => (
                      <tr key={idx}>
                        <td>+{pred.day}</td>
                        <td>{pred.date}</td>
                        <td>${pred.price.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {forecastData.predictions.length > 10 && (
                <p className="table-note">
                  Showing first 10 of {forecastData.predictions.length} predictions
                </p>
              )}
            </div>
          </div>
        )}

        {/* Comparison Results */}
        {comparisonData && !loading && (
          <div className="results-section">
            <ComparisonChart
              historicalData={comparisonData.historical_data}
              lstmPredictions={comparisonData.lstm_predictions}
              transformerPredictions={comparisonData.transformer_predictions}
              commodityInfo={comparisonData.commodity_info}
            />

            <ComparisonMetrics
              lstmMetrics={comparisonData.lstm_metrics}
              transformerMetrics={comparisonData.transformer_metrics}
              modelComparison={comparisonData.model_comparison}
              lstmPredictions={comparisonData.lstm_predictions}
              transformerPredictions={comparisonData.transformer_predictions}
            />

            <div className="predictions-comparison-table">
              <h3>📋 Side-by-Side Predictions</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Day</th>
                      <th>Date</th>
                      <th>LSTM Price</th>
                      <th>Transformer Price</th>
                      <th>Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData.lstm_predictions.slice(0, 10).map((pred, idx) => {
                      const transformerPred = comparisonData.transformer_predictions[idx];
                      const diff = Math.abs(pred.price - transformerPred.price);
                      return (
                        <tr key={idx}>
                          <td>+{pred.day}</td>
                          <td>{pred.date}</td>
                          <td>${pred.price.toFixed(2)}</td>
                          <td>${transformerPred.price.toFixed(2)}</td>
                          <td>${diff.toFixed(2)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {!forecastData && !comparisonData && !loading && (
          <div className="empty-state">
            <p>👆 Select a commodity and click "Generate Forecast" or "Compare Models" to see AI predictions</p>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;