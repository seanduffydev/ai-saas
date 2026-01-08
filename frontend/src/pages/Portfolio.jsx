import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { supabase } from '../supabaseClient';
import './Portfolio.css';

function Portfolio() {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [user, setUser] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    commodity: 'Gold',
    quantity: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const commodities = [
    'Gold', 'Silver', 'Crude Oil', 'Copper', 
    'Natural Gas', 'Platinum', 'Wheat', 'Corn'
  ];

  useEffect(() => {
    checkUser();
  }, []);

  useEffect(() => {
    if (user) {
      fetchPortfolio();
    }
  }, [user]);

  const checkUser = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    setUser(session?.user || null);
  };

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/portfolio`, {
        params: { user_id: user.id }
      });
      setPositions(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(
        `${API_URL}/api/portfolio`,
        formData,
        { params: { user_id: user.id } }
      );
      
      setShowAddForm(false);
      setFormData({
        commodity: 'Gold',
        quantity: '',
        purchase_price: '',
        purchase_date: new Date().toISOString().split('T')[0],
        notes: ''
      });
      
      fetchPortfolio();
    } catch (error) {
      console.error('Error adding position:', error);
      alert('Failed to add position');
    }
  };

  const handleDelete = async (positionId) => {
    if (!window.confirm('Are you sure you want to delete this position?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/api/portfolio/${positionId}`, {
        params: { user_id: user.id }
      });
      fetchPortfolio();
    } catch (error) {
      console.error('Error deleting position:', error);
      alert('Failed to delete position');
    }
  };

  const calculateTotals = () => {
    const totalValue = positions.reduce((sum, pos) => 
      sum + (pos.current_value || 0), 0
    );
    const totalInvested = positions.reduce((sum, pos) => 
      sum + (pos.quantity * pos.purchase_price), 0
    );
    const totalProfitLoss = totalValue - totalInvested;
    const totalProfitLossPercent = totalInvested > 0 
      ? (totalProfitLoss / totalInvested) * 100 
      : 0;

    return { totalValue, totalInvested, totalProfitLoss, totalProfitLossPercent };
  };

  if (!user) {
    return (
      <div className="portfolio-page">
        <h1>Portfolio Tracker</h1>
        <p>Please sign in to view your portfolio.</p>
      </div>
    );
  }

  const totals = calculateTotals();

  return (
    <div className="portfolio-page">
      <div className="portfolio-header">
        <h1>Portfolio Tracker</h1>
        <button 
          className="btn-add-position"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : '+ Add Position'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="portfolio-summary">
        <div className="summary-card">
          <h3>Total Invested</h3>
          <p className="summary-value">${totals.totalInvested.toFixed(2)}</p>
        </div>
        <div className="summary-card">
          <h3>Current Value</h3>
          <p className="summary-value">${totals.totalValue.toFixed(2)}</p>
        </div>
        <div className="summary-card">
          <h3>Profit/Loss</h3>
          <p className={`summary-value ${totals.totalProfitLoss >= 0 ? 'positive' : 'negative'}`}>
            ${totals.totalProfitLoss.toFixed(2)}
            <span className="percent">
              ({totals.totalProfitLossPercent.toFixed(2)}%)
            </span>
          </p>
        </div>
      </div>

      {/* Add Position Form */}
      {showAddForm && (
        <div className="add-position-form">
          <h2>Add New Position</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Commodity</label>
                <select 
                  name="commodity" 
                  value={formData.commodity}
                  onChange={handleInputChange}
                  required
                >
                  {commodities.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Quantity</label>
                <input 
                  type="number" 
                  name="quantity"
                  step="0.0001"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  placeholder="e.g., 10"
                  required
                />
              </div>

              <div className="form-group">
                <label>Purchase Price</label>
                <input 
                  type="number" 
                  name="purchase_price"
                  step="0.01"
                  value={formData.purchase_price}
                  onChange={handleInputChange}
                  placeholder="e.g., 1850.50"
                  required
                />
              </div>

              <div className="form-group">
                <label>Purchase Date</label>
                <input 
                  type="date" 
                  name="purchase_date"
                  value={formData.purchase_date}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Notes (Optional)</label>
              <textarea 
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Add any notes about this position..."
                rows="3"
              />
            </div>

            <button type="submit" className="btn-submit">Add Position</button>
          </form>
        </div>
      )}

      {/* Positions Table */}
      {loading ? (
        <p>Loading portfolio...</p>
      ) : positions.length === 0 ? (
        <div className="empty-state">
          <p>No positions yet. Add your first commodity position to get started!</p>
        </div>
      ) : (
        <div className="positions-table">
          <table>
            <thead>
              <tr>
                <th>Commodity</th>
                <th>Quantity</th>
                <th>Purchase Price</th>
                <th>Current Price</th>
                <th>Purchase Date</th>
                <th>Current Value</th>
                <th>Profit/Loss</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {positions.map(position => (
                <tr key={position.id}>
                  <td>{position.commodity}</td>
                  <td>{position.quantity}</td>
                  <td>${position.purchase_price.toFixed(2)}</td>
                  <td>
                    {position.current_price 
                      ? `$${position.current_price.toFixed(2)}`
                      : 'N/A'}
                  </td>
                  <td>{new Date(position.purchase_date).toLocaleDateString()}</td>
                  <td>
                    {position.current_value
                      ? `$${position.current_value.toFixed(2)}`
                      : 'N/A'}
                  </td>
                  <td>
                    {position.profit_loss !== null ? (
                      <span className={position.profit_loss >= 0 ? 'positive' : 'negative'}>
                        ${position.profit_loss.toFixed(2)}
                        <br />
                        ({position.profit_loss_percent.toFixed(2)}%)
                      </span>
                    ) : (
                      'N/A'
                    )}
                  </td>
                  <td>
                    <button 
                      className="btn-delete"
                      onClick={() => handleDelete(position.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Portfolio;