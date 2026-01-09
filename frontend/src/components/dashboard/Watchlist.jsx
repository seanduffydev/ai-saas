import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import './Watchlist.css';

function Watchlist({ userId }) {
  const [watchlist, setWatchlist] = useState([]);
  const [prices, setPrices] = useState({});
  const [loadingWatchlist, setLoadingWatchlist] = useState(true);
  const [loadingPrices, setLoadingPrices] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [availableCommodities, setAvailableCommodities] = useState([]);
  const [addingCommodity, setAddingCommodity] = useState(false);
  const [removingCommodity, setRemovingCommodity] = useState(null);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load watchlist from database
  const loadWatchlist = useCallback(async () => {
    if (!userId) return;

    setLoadingWatchlist(true);
    try {
      const response = await axios.get(`${API_URL}/api/watchlist?user_id=${userId}`);
      setWatchlist(response.data.map(item => item.commodity_id));
    } catch (error) {
      console.error('Error loading watchlist:', error);
      toast.error('Failed to load watchlist');
    } finally {
      setLoadingWatchlist(false);
    }
  }, [API_URL, userId]);

  // Load available commodities for add modal
  const loadAvailableCommodities = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/commodities`);
      setAvailableCommodities(response.data.commodities);
    } catch (error) {
      console.error('Error loading commodities:', error);
    }
  }, [API_URL]);

  // Load prices sequentially to avoid ANY closure issues
  const loadPrices = useCallback(async () => {
    if (watchlist.length === 0) {
      setPrices({});
      return;
    }

    setLoadingPrices(true);

    try {
      const newPriceData = {};

      // Fetch each commodity one at a time
      for (let i = 0; i < watchlist.length; i++) {
        const commodityId = watchlist[i];
        
        try {
          const response = await axios.get(`${API_URL}/api/prices/${commodityId}?period=5d`);
          const data = response.data.data;

          if (data && data.length >= 2) {
            const latest = data[data.length - 1];
            const previous = data[data.length - 2];
            const change = ((latest.close - previous.close) / previous.close) * 100;

            // Explicitly set this commodity's data
            newPriceData[commodityId] = {
              price: latest.close,
              change: change,
              info: response.data.commodity_info
            };
          }
        } catch (error) {
          console.error(`Error loading ${commodityId}:`, error);
        }
      }

      // Set all prices at once
      setPrices(newPriceData);
    } catch (error) {
      console.error('Error loading prices:', error);
      toast.error('Failed to load prices');
    } finally {
      setLoadingPrices(false);
    }
  }, [API_URL, watchlist]);



  // Initial load
  useEffect(() => {
    if (userId) {
      loadWatchlist();
      loadAvailableCommodities();
    }
  }, [userId, loadWatchlist, loadAvailableCommodities]);

  // Load prices when watchlist changes
  useEffect(() => {
    if (watchlist.length > 0) {
      loadPrices();
      // Refresh prices every 5 minutes
      const interval = setInterval(loadPrices, 5 * 60 * 1000);
      return () => clearInterval(interval);
    } else {
      setPrices({});
    }
  }, [watchlist, loadPrices]);

  // Navigate to forecast page (card click handler)
  const handleCardClick = (commodity) => {
    navigate('/forecast', { state: { commodity } });
  };

  // Helper function to format commodity name
  const getCommodityName = (id) => {
    return id.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  // Get icon for commodity
  const getIcon = (commodity) => {
    const icons = {
      gold: '🥇',
      silver: '🥈',
      crude_oil: '🛢️',
      copper: '🔶',
      natural_gas: '⚡',
      platinum: '⚪',
      wheat: '🌾',
      corn: '🌽',
      soybeans: '🫘'
    };
    return icons[commodity] || '📊';
  };

  // Get suggested commodities for new users
  const getSuggestedCommodities = () => {
    const suggestions = [
      { id: 'gold', name: 'Gold', icon: '🥇' },
      { id: 'silver', name: 'Silver', icon: '🥈' },
      { id: 'crude_oil', name: 'Crude Oil', icon: '🛢️' }
    ];

    // Only return suggestions that are actually available
    return suggestions.filter(suggestion =>
      availableCommodities.some(c => c.id === suggestion.id)
    );
  };

  // Add commodity to watchlist
  const handleAddCommodity = async (commodityId) => {
    setAddingCommodity(true);
    try {
      await axios.post(
        `${API_URL}/api/watchlist?user_id=${userId}`,
        { commodity_id: commodityId }
      );

      toast.success(`${getCommodityName(commodityId)} added to watchlist`);
      await loadWatchlist();
      setShowAddModal(false);
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error('This commodity is already in your watchlist');
      } else {
        console.error('Error adding commodity:', error);
        toast.error('Failed to add commodity to watchlist');
      }
    } finally {
      setAddingCommodity(false);
    }
  };

  // Remove commodity from watchlist
  const handleRemoveCommodity = async (e, commodityId) => {
    e.stopPropagation(); // Prevent card click

    setRemovingCommodity(commodityId);
    try {
      await axios.delete(`${API_URL}/api/watchlist/${commodityId}?user_id=${userId}`);

      toast.success(`${getCommodityName(commodityId)} removed from watchlist`);
      await loadWatchlist();
    } catch (error) {
      console.error('Error removing commodity:', error);
      toast.error('Failed to remove commodity');
    } finally {
      setRemovingCommodity(null);
    }
  };

  // Get commodities not in watchlist
  const commoditiesNotInWatchlist = availableCommodities.filter(
    c => !watchlist.includes(c.id)
  );

  // Render skeleton loaders
  const renderSkeletons = () => (
    <div className="watchlist-items">
      {[1, 2, 3].map(i => (
        <div key={i} className="watchlist-item skeleton">
          <div className="watchlist-item-left">
            <div className="skeleton-icon"></div>
            <div className="watchlist-info">
              <div className="skeleton-text skeleton-name"></div>
              <div className="skeleton-text skeleton-price"></div>
            </div>
          </div>
          <div className="watchlist-item-right">
            <div className="skeleton-text skeleton-change"></div>
          </div>
        </div>
      ))}
    </div>
  );

  // Loading state
  if (loadingWatchlist) {
    return (
      <div className="watchlist-card">
        <div className="watchlist-header">
          <h3>📊 Your Watchlist</h3>
        </div>
        {renderSkeletons()}
      </div>
    );
  }

  return (
    <>
      <Toaster position="top-right" />
      <div className="watchlist-card">
        <div className="watchlist-header">
          <h3>📊 Your Watchlist</h3>
          <button
            className="refresh-btn"
            onClick={loadPrices}
            disabled={loadingPrices}
            title="Refresh prices"
          >
            {loadingPrices ? '⏳' : '🔄'}
          </button>
        </div>

        {watchlist.length === 0 ? (
          <div className="watchlist-empty">
            <div className="empty-icon">📊</div>
            <h4>Your watchlist is empty</h4>
            <p>Add commodities to track their prices and generate forecasts</p>

            {/* Suggested Commodities Section */}
            <div className="suggested-section">
              <div className="suggested-header">
                <span className="suggested-icon">✨</span>
                <span className="suggested-text">Suggested to start with:</span>
              </div>

              <div className="suggested-commodities">
                {getSuggestedCommodities().map((commodity) => (
                  <button
                    key={commodity.id}
                    className="suggested-commodity-btn"
                    onClick={() => handleAddCommodity(commodity.id)}
                    disabled={addingCommodity}
                  >
                    <span className="suggested-commodity-icon">{commodity.icon}</span>
                    <span className="suggested-commodity-name">{commodity.name}</span>
                  </button>
                ))}
              </div>

              <div className="suggested-divider">
                <span>or browse all</span>
              </div>
            </div>

            <button className="add-watchlist-btn" onClick={() => setShowAddModal(true)}>
              + Browse All Commodities
            </button>
          </div>
        ) : (
          <>
            {loadingPrices && watchlist.length > 0 ? (
              renderSkeletons()
            ) : (
              <div className="watchlist-items">
                {watchlist.map((commodity) => {
                  const data = prices[commodity];
                  if (!data) return null;

                  const isPositive = data.change >= 0;

                  return (
                    <div
                      key={commodity}
                      className="watchlist-item clickable"
                      onClick={() => handleCardClick(commodity)}
                    >
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
                      </div>

                      <button
                        className="remove-btn-corner"
                        onClick={(e) => handleRemoveCommodity(e, commodity)}
                        disabled={removingCommodity === commodity}
                        title="Remove from watchlist"
                      >
                        {removingCommodity === commodity ? '...' : '✕'}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}

            <button
              className="add-watchlist-btn"
              onClick={() => setShowAddModal(true)}
              disabled={commoditiesNotInWatchlist.length === 0}
            >
              {commoditiesNotInWatchlist.length === 0
                ? '✓ All commodities added'
                : '+ Add More Commodities'
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
                  <div className="modal-empty">
                    <p>🎉 All commodities are already in your watchlist!</p>
                  </div>
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
    </>
  );
}

export default Watchlist;
