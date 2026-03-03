/**
 * @fileoverview Root app component: auth, routing, and layout for Commodity Forecasting Lab.
 */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from './supabaseClient';
import './App.css';

import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import ForecastPage from './pages/ForecastPage';
import NewsPage from './pages/NewsPage';
import Portfolio from './pages/Portfolio';

/**
 * Main application component. Handles Supabase auth and routes authenticated
 * users to Dashboard, Forecast, News, and Portfolio. Unauthenticated users see
 * sign-in/sign-up form.
 * @return {JSX.Element} Either auth UI, loading spinner, or routed app with Layout.
 */
function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check authentication
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  /**
   * Handle sign-up form submit. Creates Supabase user and prompts email confirmation.
   * @param {React.FormEvent} e - Form submit event.
   */
  const handleSignUp = async (e) => {
    e.preventDefault();
    setError(null);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setError(error.message);
    } else {
      alert('Check your email for confirmation!');
    }
  };

  /**
   * Handle sign-in form submit. Authenticates with Supabase email/password.
   * @param {React.FormEvent} e - Form submit event.
   */
  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
    }
  };

  /** Sign out the current user via Supabase auth. */
  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  // Loading state
  if (loading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Login/Signup UI
  if (!user) {
    return (
      <div className="App">
        <div className="auth-container">
          <h1>📈 Commodity Forecasting Lab</h1>
          <p className="subtitle">AI-Powered LSTM Price Predictions</p>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={isSignUp ? handleSignUp : handleSignIn}>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password (min 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit" className="primary-button">
              {isSignUp ? 'Sign Up' : 'Sign In'}
            </button>
          </form>

          <div className="auth-toggle">
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}
            {' '}
            <button onClick={() => setIsSignUp(!isSignUp)} className="link-button">
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main app with routing
  return (
    <Router>
      <Layout user={user} onSignOut={handleSignOut}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/forecast" element={<ForecastPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;