/**
 * @fileoverview Portfolio summary card for dashboard: total value, P&L, link to portfolio.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { supabase } from '../../supabaseClient';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function PortfolioSummary() {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const getAuthHeaders = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
  }, []);

  const fetchPortfolio = useCallback(async () => {
    try {
      setError(null);
      const headers = await getAuthHeaders();
      const response = await axios.get(`${API_URL}/api/portfolio`, { headers });
      setPositions(response.data || []);
    } catch (err) {
      console.error('Error loading portfolio summary:', err);
      setError(err.message);
      setPositions([]);
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  const totalValue = positions.reduce((sum, pos) => sum + (pos.current_value || 0), 0);
  const totalInvested = positions.reduce((sum, pos) => sum + (pos.quantity * pos.purchase_price), 0);
  const profitLoss = totalValue - totalInvested;
  const pnlClass = profitLoss > 0 ? 'positive' : profitLoss < 0 ? 'negative' : 'neutral';

  const formatMoney = (n) => {
    if (n == null || Number.isNaN(n)) return '$0.00';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n);
  };

  const handleViewPortfolio = () => {
    navigate('/portfolio');
  };

  return (
    <div className="dashboard-card-new">
      <h3>💼 Portfolio Summary</h3>
      {loading && (
        <p className="placeholder-text">Loading...</p>
      )}
      {!loading && error && (
        <p className="placeholder-text">Unable to load portfolio</p>
      )}
      {!loading && !error && positions.length === 0 && (
        <>
          <p className="placeholder-text">No positions yet</p>
          <div className="stat-row">
            <span className="stat-label">Total Value:</span>
            <span className="stat-value">$0.00</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">P&L:</span>
            <span className="stat-value neutral">$0.00</span>
          </div>
        </>
      )}
      {!loading && !error && positions.length > 0 && (
        <>
          <div className="stat-row">
            <span className="stat-label">Total Value:</span>
            <span className="stat-value">{formatMoney(totalValue)}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">P&L:</span>
            <span className={`stat-value ${pnlClass}`}>{formatMoney(profitLoss)}</span>
          </div>
        </>
      )}
      <button type="button" className="view-btn" onClick={handleViewPortfolio}>
        View Portfolio →
      </button>
    </div>
  );
}

export default PortfolioSummary;
