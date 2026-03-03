/**
 * @fileoverview Main app layout: sidebar, header, and content area.
 */

import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

/**
 * Wraps the app content with sidebar navigation and header.
 * @param {Object} props - Component props.
 * @param {Object} [props.user] - Current auth user (for header).
 * @param {function} [props.onSignOut] - Callback when user signs out.
 * @param {React.ReactNode} props.children - Page content to render in main area.
 * @return {JSX.Element} Layout with sidebar, header, and main content.
 */
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