import React from 'react';

function MetricsDisplay({ metrics, modelInfo, predictions }) {
  if (!metrics || !modelInfo) {
    return null;
  }

  const lastHistoricalPrice = predictions && predictions.length > 0 ? 
    predictions[0].price : null;
  const lastPredictedPrice = predictions && predictions.length > 0 ? 
    predictions[predictions.length - 1].price : null;
  
  const priceChange = lastHistoricalPrice && lastPredictedPrice ? 
    ((lastPredictedPrice - lastHistoricalPrice) / lastHistoricalPrice * 100).toFixed(2) : null;

  return (
    <div className="metrics-display">
      <h3>📊 Forecast Results</h3>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Model Type</div>
          <div className="metric-value">{modelInfo.type}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Training Time</div>
          <div className="metric-value">{metrics.training_time?.toFixed(2)}s</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Training Loss</div>
          <div className="metric-value">{metrics.training_loss?.toFixed(6)}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Data Points Used</div>
          <div className="metric-value">{metrics.data_points_used}</div>
        </div>

        {priceChange && (
          <div className="metric-card">
            <div className="metric-label">Predicted Change</div>
            <div className={`metric-value ${priceChange > 0 ? 'positive' : 'negative'}`}>
              {priceChange > 0 ? '↑' : '↓'} {Math.abs(priceChange)}%
            </div>
          </div>
        )}

        <div className="metric-card">
          <div className="metric-label">Forecast Horizon</div>
          <div className="metric-value">{predictions?.length || 0} days</div>
        </div>
      </div>
    </div>
  );
}

export default MetricsDisplay;