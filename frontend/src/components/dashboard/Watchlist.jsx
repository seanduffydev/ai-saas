import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Watchlist.css';

function Watchlist({ userId }) {
  const [watchlist, setWatchlist] = useState([]);
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [availableCommodities, setAvailableCommodities] = useState([]);
  const [addingCommodity, setAddingCommodity] = useState(false);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadWatchlist();
    loadAvailableCommodities();
  }, [userId]);

  useEffect(() => {
    if (watchlist.length > 0) {
      loadPrices();
      // Refresh prices every 5 minutes
      const interval = setInterval(loadPrices, 5 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [watchlist]);

  const loadWatchlist = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/watchlist?user_id=${userId}`);

      if (response.data.length === 0) {
        // Initialize default watchlist for new users
        await axios.post(`${API_URL}/api/watchlist/initialize?user_id=${userId}`);
        // Reload watchlist
        const reloadResponse = await axios.get(`${API_URL}/api/watchlist?user_id=${userId}`);
        setWatchlist(reloadResponse.data.map(item => item.commodity_id));
      } else {
        setWatchlist(response.data.map(item => item.commodity_id));
      }
    } catch (error) {
      console.error('Error loading watchlist:', error);
    }
  };

  const loadAvailableCommodities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/commodities`);
      setAvailableCommodities(response.data.commodities);
    } catch (error) {
      console.error('Error loading commodities:', error);
    }
  };

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

  const handleAddCommodity = async (commodityId) => {
    setAddingCommodity(true);
    try {
      await axios.post(
        `${API_URL}/api/watchlist?user_id=${userId}`,
        { commodity_id: commodityId }
      );

      // Reload watchlist
      await loadWatchlist();
      setShowAddModal(false);
    } catch (error) {
      if (error.response?.status === 400) {
        alert('This commodity is already in your watchlist');
      } else {
        console.error('Error adding commodity:', error);
        alert('Failed to add commodity to watchlist');
      }
    } finally {
      setAddingCommodity(false);
    }
  };

  const handleRemoveCommodity = async (commodityId) => {
    if (!window.confirm(`Remove ${getCommodityName(commodityId)} from watchlist?`)) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/api/watchlist/${commodityId}?user_id=${userId}`);

      // Reload watchlist
      await loadWatchlist();
    } catch (error) {
      console.error('Error removing commodity:', error);
      alert('Failed to remove commodity from watchlist');
    }
  };

  if (loading && watchlist.length === 0) {
    return (
      <div className="watchlist-card">
        <h3>📊 Your Watchlist</h3>
        <div className="watchlist-loading">Loading watchlist...</div>
      </div>
    );
  }

  // Get commodities not in watchlist for the add modal
  const commoditiesNotInWatchlist = availableCommodities.filter(
    c => !watchlist.includes(c.id)
  );

  return (
    <div className="watchlist-card">
      <div className="watchlist-header">
        <h3>📊 Your Watchlist</h3>
        <button className="refresh-btn" onClick={loadPrices}>🔄</button>
      </div>

      {watchlist.length === 0 ? (
        <div className="watchlist-empty">
          <p>Your watchlist is empty</p>
          <button className="add-watchlist-btn" onClick={() => setShowAddModal(true)}>
            + Add Commodity
          </button>
        </div>
      ) : (
        <>
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
                    <div className="watchlist-actions">
                      <button
                        className="forecast-btn-small"
                        onClick={() => handleForecast(commodity)}
                      >
                        Forecast
                      </button>
                      <button
                        className="remove-btn-small"
                        onClick={() => handleRemoveCommodity(commodity)}
                        title="Remove from watchlist"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <button
            className="add-watchlist-btn"
            onClick={() => setShowAddModal(true)}
            disabled={commoditiesNotInWatchlist.length === 0}
          >
            {commoditiesNotInWatchlist.length === 0
              ? 'All commodities added'
              : '+ Add to Watchlist'
            }
          </button>
        </>
      )}

      {/* Add Commodity Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add to Watchlist</h3>
              <button className="modal-close" onClick={() => setShowAddModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              {commoditiesNotInWatchlist.length === 0 ? (
                <p>All commodities are already in your watchlist!</p>
              ) : (
                <div className="commodity-grid">
                  {commoditiesNotInWatchlist.map((commodity) => (
                    <button
                      key={commodity.id}
                      className="commodity-card"
                      onClick={() => handleAddCommodity(commodity.id)}
                      disabled={addingCommodity}
                    >
                      <span className="commodity-icon">{commodity.icon}</span>
                      <div className="commodity-name">{commodity.name}</div>
                      <div className="commodity-category">{commodity.category}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Watchlist;