import React from 'react';

function ComparisonMetrics({ lstmMetrics, transformerMetrics, modelComparison, lstmPredictions, transformerPredictions }) {
  if (!lstmMetrics || !transformerMetrics) {
    return null;
  }

  const lastHistoricalPrice = lstmPredictions && lstmPredictions.length > 0 ? 
    lstmPredictions[0].price : null;
  
  const lstmLastPrice = lstmPredictions && lstmPredictions.length > 0 ? 
    lstmPredictions[lstmPredictions.length - 1].price : null;
  const transformerLastPrice = transformerPredictions && transformerPredictions.length > 0 ? 
    transformerPredictions[transformerPredictions.length - 1].price : null;
  
  const lstmChange = lastHistoricalPrice && lstmLastPrice ? 
    ((lstmLastPrice - lastHistoricalPrice) / lastHistoricalPrice * 100).toFixed(2) : null;
  const transformerChange = lastHistoricalPrice && transformerLastPrice ? 
    ((transformerLastPrice - lastHistoricalPrice) / lastHistoricalPrice * 100).toFixed(2) : null;

  return (
    <div className="metrics-display">
      <h3>📊 Model Comparison Results</h3>
      
      <div className="comparison-grid">
        <div className="model-section">
          <h4>🔴 LSTM Model</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Training Time</div>
              <div className="metric-value">{lstmMetrics.training_time?.toFixed(2)}s</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Training Loss</div>
              <div className="metric-value">{lstmMetrics.training_loss?.toFixed(6)}</div>
            </div>
            {lstmChange && (
              <div className="metric-card">
                <div className="metric-label">Predicted Change</div>
                <div className={`metric-value ${lstmChange > 0 ? 'positive' : 'negative'}`}>
                  {lstmChange > 0 ? '↑' : '↓'} {Math.abs(lstmChange)}%
                </div>
              </div>
            )}
            <div className="metric-card">
              <div className="metric-label">Avg Predicted Price</div>
              <div className="metric-value">${modelComparison?.lstm_avg_price?.toFixed(2)}</div>
            </div>
          </div>
        </div>

        <div className="model-section">
          <h4>🔵 Transformer Model</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Training Time</div>
              <div className="metric-value">{transformerMetrics.training_time?.toFixed(2)}s</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Training Loss</div>
              <div className="metric-value">{transformerMetrics.training_loss?.toFixed(6)}</div>
            </div>
            {transformerChange && (
              <div className="metric-card">
                <div className="metric-label">Predicted Change</div>
                <div className={`metric-value ${transformerChange > 0 ? 'positive' : 'negative'}`}>
                  {transformerChange > 0 ? '↑' : '↓'} {Math.abs(transformerChange)}%
                </div>
              </div>
            )}
            <div className="metric-card">
              <div className="metric-label">Avg Predicted Price</div>
              <div className="metric-value">${modelComparison?.transformer_avg_price?.toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="comparison-summary">
        <h4>📈 Summary</h4>
        <p>
          <strong>Speed Winner:</strong> {lstmMetrics.training_time < transformerMetrics.training_time ? 'LSTM' : 'Transformer'} 
          {' '}({Math.min(lstmMetrics.training_time, transformerMetrics.training_time).toFixed(2)}s)
        </p>
        <p>
          <strong>Accuracy Winner:</strong> {lstmMetrics.training_loss < transformerMetrics.training_loss ? 'LSTM' : 'Transformer'}
          {' '}(lower loss: {Math.min(lstmMetrics.training_loss, transformerMetrics.training_loss).toFixed(6)})
        </p>
        <p>
          <strong>Prediction Difference:</strong> ${modelComparison?.difference?.toFixed(2)}
        </p>
      </div>
    </div>
  );
}

export default ComparisonMetrics;