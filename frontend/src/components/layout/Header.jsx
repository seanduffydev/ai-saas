import React from 'react';
import './Header.css';

function Header({ user, onSignOut }) {
  return (
    <header className="app-header-new">
      <div className="header-content-new">
        <div className="header-left">
          <h1 className="page-title">Welcome back! 👋</h1>
        </div>
        
        <div className="header-right">
          <span className="user-email">{user?.email}</span>
          <button onClick={onSignOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;