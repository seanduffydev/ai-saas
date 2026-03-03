/**
 * @fileoverview Dashboard page: welcome, watchlist, portfolio summary, quick actions.
 */

import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import Watchlist from '../components/dashboard/Watchlist';
import PortfolioSummary from '../components/dashboard/PortfolioSummary';
import QuickActions from '../components/dashboard/QuickActions';
import './DashboardPage.css';

/**
 * Dashboard page component. Shows welcome section, user watchlist, portfolio
 * summary placeholder, and quick action buttons.
 * @return {JSX.Element} Dashboard layout with watchlist and sidebar cards.
 */
function DashboardPage() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkUser();
  }, []);

  /** Fetches current session and sets user state. */
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
          <PortfolioSummary />
          <QuickActions />
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