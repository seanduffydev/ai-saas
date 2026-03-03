import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './NewsPage.css';

function NewsPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCommodity, setSelectedCommodity] = useState('all');
  const [commodities] = useState([
    { id: 'all', name: 'All Commodities', icon: '📊' },
    { id: 'gold', name: 'Gold', icon: '🥇' },
    { id: 'silver', name: 'Silver', icon: '🥈' },
    { id: 'crude_oil', name: 'Crude Oil', icon: '🛢️' },
    { id: 'copper', name: 'Copper', icon: '🔶' },
    { id: 'natural_gas', name: 'Natural Gas', icon: '⚡' },
  ]);
  const [isCached, setIsCached] = useState(false);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const loadNews = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
        let url = '';
        if (selectedCommodity === 'all') {
        url = `${API_URL}/api/news?limit=20`;
        } else {
        url = `${API_URL}/api/news/${selectedCommodity}?limit=10`;
        }

        const response = await axios.get(url);
        
        // Check if articles is an array
        const articlesData = response.data.articles;
        if (Array.isArray(articlesData)) {
        setNews(articlesData);
        } else {
        // If it's a JSON string, parse it
        setNews(JSON.parse(articlesData));
        }
    
        setIsCached(response.data.cached || false);
    } catch (err) {
        console.error('Error loading news:', err);
        setError('Failed to load news. Please try again.');
        setNews([]);  // Set empty array on error
    } finally {
        setLoading(false);
    }
  }, [selectedCommodity, API_URL]);

  useEffect(() => {
    loadNews();
  }, [loadNews]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Recently';
    
    // Alpha Vantage format: "20250107T123000"
    const year = dateString.substring(0, 4);
    const month = dateString.substring(4, 6);
    const day = dateString.substring(6, 8);
    
    const date = new Date(`${year}-${month}-${day}`);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="news-page-container">
      <div className="page-header">
        <h2>📰 News & Market Intelligence</h2>
        <p>Stay updated with the latest commodity market news and sentiment analysis</p>
      </div>

      <div className="news-filters">
        <div className="filter-group">
          <label>Filter by Commodity:</label>
          <select 
            value={selectedCommodity}
            onChange={(e) => setSelectedCommodity(e.target.value)}
            disabled={loading}
          >
            {commodities.map(comm => (
              <option key={comm.id} value={comm.id}>
                {comm.icon} {comm.name}
              </option>
            ))}
          </select>
        </div>

        <button onClick={loadNews} disabled={loading} className="refresh-news-btn">
          🔄 Refresh
        </button>
      </div>

      {isCached && (
        <div className="cache-indicator">
            ⚡ Loaded from cache (refreshes every 4 hours)
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {loading && (
        <div className="news-loading">
          <div className="spinner"></div>
          <p>Loading news...</p>
        </div>
      )}

      {!loading && news.length === 0 && (
        <div className="no-news">
          <p>No news articles found. Try selecting a different commodity.</p>
        </div>
      )}

      <div className="news-grid">
        {news.map((article, index) => (
          <a 
            key={index}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="news-card"
          >
            {article.image_url && (
              <img 
                src={article.image_url} 
                alt={article.title}
                className="news-image"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            )}
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">{article.source}</span>
                <span className={`sentiment-badge ${article.sentiment || 'neutral'}`}>
                  {article.sentiment_label || '🟡 Neutral'}
                </span>
              </div>
              <h3 className="news-title">{article.title}</h3>
              <p className="news-description">{article.description}</p>
              <div className="news-footer">
                <span className="news-date">{formatDate(article.published_at)}</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

export default NewsPage;