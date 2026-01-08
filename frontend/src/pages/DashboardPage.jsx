import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient'; // ← ADD THIS IMPORT
import Watchlist from '../components/dashboard/Watchlist';
import './DashboardPage.css';

function DashboardPage() {
  const [user, setUser] = useState(null); // ← ADD THIS

  // Get the current user when component loads
  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    setUser(session?.user || null);
  };

  return (
    <div className="dashboard-page-new">
      <div className="welcome-section-new">
        <h2>👋 Welcome to Commodity Trading Lab</h2>
        <p>Your AI-powered platform for commodity market analysis</p>
      </div>

      <div className="dashboard-grid-new">
        <div className="dashboard-main">
          <Watchlist userId={user?.id} /> {/* ← CHANGED THIS LINE */}
        </div>

        <div className="dashboard-sidebar">
          <div className="dashboard-card-new">
            <h3>💼 Portfolio Summary</h3>
            <p className="placeholder-text">Track your positions</p>
            <div className="stat-row">
              <span className="stat-label">Total Value:</span>
              <span className="stat-value">$0.00</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Today's P&L:</span>
              <span className="stat-value neutral">$0.00</span>
            </div>
            <button className="view-btn">View Portfolio →</button>
          </div>

          <div className="dashboard-card-new">
            <h3>🚀 Quick Actions</h3>
            <button className="quick-action-btn">📊 Generate Forecast</button>
            <button className="quick-action-btn">📰 Check Latest News</button>
            <button className="quick-action-btn">💼 Add to Portfolio</button>
          </div>
        </div>
      </div>

      <div className="dashboard-info-card">
        <h3>📚 New to Commodity Trading?</h3>
        <p>
          Start by adding commodities to your watchlist, then generate AI forecasts to see 
          predicted price movements. Track paper trades in your portfolio to learn without risk!
        </p>
        <button className="learn-more-btn">Learn More →</button>
      </div>
    </div>
  );
}

export default DashboardPage;