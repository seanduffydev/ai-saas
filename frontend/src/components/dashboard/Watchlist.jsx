import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Watchlist.css';

function Watchlist({ userId }) {
  const [watchlist, setWatchlist] = useState(['gold', 'silver', 'crude_oil', 'copper']);
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadPrices();
    // Refresh prices every 5 minutes
    const interval = setInterval(loadPrices, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [watchlist]);

  const loadPrices = async () => {
    setLoading(true);
    const priceData = {};

    for (const commodity of watchlist) {
      try {
        const response = await axios.get(`${API_URL}/api/prices/${commodity}?period=5d`);
        const data = response.data.data;
        
        if (data && data.length >= 2) {
          const latest = data[data.length - 1];
          const previous = data[data.length - 2];
          const change = ((latest.close - previous.close) / previous.close) * 100;
          
          priceData[commodity] = {
            price: latest.close,
            change: change,
            info: response.data.commodity_info
          };
        }
      } catch (error) {
        console.error(`Error loading ${commodity}:`, error);
      }
    }

    setPrices(priceData);
    setLoading(false);
  };

  const handleForecast = (commodity) => {
    navigate('/forecast', { state: { commodity } });
  };

  const getCommodityName = (id) => {
    return id.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getIcon = (commodity) => {
    const icons = {
      gold: '🥇',
      silver: '🥈',
      crude_oil: '🛢️',
      copper: '🔶',
      natural_gas: '⚡',
      wheat: '🌾',
      corn: '🌽',
      soybeans: '🫘'
    };
    return icons[commodity] || '📊';
  };

  if (loading) {
    return (
      <div className="watchlist-card">
        <h3>📊 Your Watchlist</h3>
        <div className="watchlist-loading">Loading prices...</div>
      </div>
    );
  }

  return (
    <div className="watchlist-card">
      <div className="watchlist-header">
        <h3>📊 Your Watchlist</h3>
        <button className="refresh-btn" onClick={loadPrices}>🔄</button>
      </div>

      <div className="watchlist-items">
        {watchlist.map((commodity) => {
          const data = prices[commodity];
          if (!data) return null;

          const isPositive = data.change >= 0;

          return (
            <div key={commodity} className="watchlist-item">
              <div className="watchlist-item-left">
                <span className="watchlist-icon">{getIcon(commodity)}</span>
                <div className="watchlist-info">
                  <div className="watchlist-name">{getCommodityName(commodity)}</div>
                  <div className="watchlist-price">${data.price.toFixed(2)}</div>
                </div>
              </div>

              <div className="watchlist-item-right">
                <div className={`watchlist-change ${isPositive ? 'positive' : 'negative'}`}>
                  {isPositive ? '↑' : '↓'} {Math.abs(data.change).toFixed(2)}%
                </div>
                <button 
                  className="forecast-btn-small"
                  onClick={() => handleForecast(commodity)}
                >
                  Forecast
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <button className="add-watchlist-btn">+ Add to Watchlist</button>
    </div>
  );
}

export default Watchlist;