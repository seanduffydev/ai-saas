import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

function Layout({ user, onSignOut, children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-wrapper">
        <Header user={user} onSignOut={onSignOut} />
        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;