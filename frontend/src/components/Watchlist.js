import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import Toast from './Toast';

function Watchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const response = await api.getWatchlist();
      setWatchlist(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!symbol.trim()) return;

    setLoading(true);
    try {
      await api.addToWatchlist({ symbol: symbol.toUpperCase() });
      setToast({ message: '✅ Added to watchlist!', type: 'success' });
      setSymbol('');
      fetchWatchlist();
    } catch (error) {
      setToast({ message: error.message || 'Failed to add', type: 'error' });
    }
    setLoading(false);
  };

  const handleRemove = async (id) => {
    try {
      await api.removeFromWatchlist(id);
      setToast({ message: 'Removed from watchlist', type: 'success' });
      fetchWatchlist();
    } catch (error) {
      setToast({ message: 'Failed to remove', type: 'error' });
    }
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="watchlist-section">
        <h2>⭐ Stock Watchlist</h2>
        
        <form onSubmit={handleAdd} className="watchlist-form">
          <input
            type="text"
            placeholder="Enter stock symbol (e.g., AAPL)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? '⏳ Adding...' : '➕ Add to Watchlist'}
          </button>
        </form>

        {watchlist.length === 0 ? (
          <div className="empty-state">
            <p>⭐ No stocks in watchlist</p>
            <p>Add stocks to track their prices</p>
          </div>
        ) : (
          <div className="watchlist-grid">
            {watchlist.map((item) => (
              <div key={item.id} className="watchlist-card">
                <div className="watchlist-header">
                  <h3>{item.symbol}</h3>
                  <button onClick={() => handleRemove(item.id)}>×</button>
                </div>
                <div className="watchlist-price">
                  ${item.current_price.toLocaleString()}
                </div>
                <div className="watchlist-date">
                  Added: {new Date(item.added_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

export default Watchlist;