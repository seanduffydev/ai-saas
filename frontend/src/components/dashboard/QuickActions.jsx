/**
 * @fileoverview Quick action buttons for dashboard: forecast, news, add to portfolio.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

function QuickActions() {
  const navigate = useNavigate();

  const handleGenerateForecast = () => {
    navigate('/forecast');
  };

  const handleCheckNews = () => {
    navigate('/news');
  };

  const handleAddToPortfolio = () => {
    navigate('/portfolio', { state: { openAddForm: true } });
  };

  return (
    <div className="dashboard-card-new">
      <h3>🚀 Quick Actions</h3>
      <button type="button" className="quick-action-btn" onClick={handleGenerateForecast}>
        📊 Generate Forecast
      </button>
      <button type="button" className="quick-action-btn" onClick={handleCheckNews}>
        📰 Check Latest News
      </button>
      <button type="button" className="quick-action-btn" onClick={handleAddToPortfolio}>
        💼 Add to Portfolio
      </button>
    </div>
  );
}

export default QuickActions;
