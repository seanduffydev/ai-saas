/**
 * @fileoverview Sidebar navigation with links to Dashboard, Forecast, News, Portfolio, Help.
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

/**
 * Renders the main sidebar with brand and nav links. Uses NavLink for active styling.
 * @return {JSX.Element} Sidebar nav element.
 */
function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-logo">📈 Commodity Lab</h2>
        <p className="sidebar-tagline">AI-Powered Trading</p>
      </div>

      <div className="sidebar-nav">
        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          <span className="nav-icon">🏠</span>
          <span className="nav-text">Dashboard</span>
        </NavLink>

        <NavLink 
          to="/forecast" 
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          <span className="nav-icon">🔮</span>
          <span className="nav-text">AI Forecast</span>
        </NavLink>

        <NavLink 
          to="/news" 
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          <span className="nav-icon">📰</span>
          <span className="nav-text">News</span>
        </NavLink>

        <NavLink 
          to="/portfolio" 
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          <span className="nav-icon">💼</span>
          <span className="nav-text">Portfolio</span>
        </NavLink>
      </div>

      <div className="sidebar-footer">
        <NavLink 
          to="/help" 
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          <span className="nav-icon">❓</span>
          <span className="nav-text">Help</span>
        </NavLink>
      </div>
    </nav>
  );
}

export default Sidebar;