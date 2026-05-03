import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import Toast from './Toast';

function PaperTrading() {
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  // ✅ FIX ADDED HERE

  const [formData, setFormData] = useState({
    symbol: '',
    trade_type: 'buy',
    quantity: '',
    user_id: 1,
    notes: ''
  });

  useEffect(() => {
    fetchPortfolio();
    fetchTrades();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const response = await api.getPaperPortfolio(1);
      setPortfolio(response.data);
    } catch (error) {
      console.error(error);
      setToast({ message: 'Failed to load portfolio', type: 'error' });
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await api.getPaperTrades(1, 20);
      setTrades(response.data);
    } catch (error) {
      console.error('Error fetching trades:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.symbol.trim()) {
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return;
    }

    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      setToast({ message: 'Quantity must be greater than 0', type: 'error' });
      return;
    }

    setLoading(true);

    try {
      const response = await api.executePaperTrade({
        ...formData,
        quantity: parseFloat(formData.quantity)
      });

      if (response.data.success) {
        setToast({
          message: `✅ ${formData.trade_type.toUpperCase()} order executed!`,
          type: 'success'
        });
        setFormData({ symbol: '', trade_type: 'buy', quantity: '', user_id: 1, notes: '' });
        fetchPortfolio();
        fetchTrades();
      }
      setLoading(false);
    } catch (error) {
      setToast({
        message: error.response?.data?.detail || 'Trade execution failed',
        type: 'error'
      });
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('⚠️ Are you sure you want to reset your paper trading portfolio? This will delete all trades and reset your balance to $100,000.')) {
      try {
        await api.resetPaperPortfolio(1);
        setToast({ message: '✅ Portfolio reset successfully!', type: 'success' });
        fetchPortfolio();
        fetchTrades();
      } catch (error) {
        setToast({ message: 'Error resetting portfolio', type: 'error' });
      }
    }
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="paper-trading-section">
        <div className="paper-header">
          <div>
            <h2>💰 Paper Trading Simulator</h2>
            <p className="section-description">
              Practice trading with virtual money. No risk, real learning!
            </p>
          </div>
          <button onClick={handleReset} className="reset-button">
            🔄 Reset Portfolio
          </button>
        </div>

        {/* Portfolio Summary */}
        {portfolio && (
          <div className="paper-portfolio-summary">
            <div className="summary-cards">
              <div className="paper-summary-card cash">
                <div className="card-icon">💵</div>
                <div className="card-content">
                  <div className="card-label">Available Cash</div>
                  <div className="card-value">${portfolio.total_cash.toLocaleString()}</div>
                </div>
              </div>

              <div className="paper-summary-card holdings">
                <div className="card-icon">📊</div>
                <div className="card-content">
                  <div className="card-label">Holdings Value</div>
                  <div className="card-value">${portfolio.holdings_value?.toLocaleString() || '0'}</div>
                </div>
              </div>

              <div className="paper-summary-card total">
                <div className="card-icon">💼</div>
                <div className="card-content">
                  <div className="card-label">Total Portfolio Value</div>
                  <div className="card-value">${portfolio.portfolio_value.toLocaleString()}</div>
                </div>
              </div>

              <div className={`paper-summary-card profit ${portfolio.total_profit_loss >= 0 ? 'positive' : 'negative'}`}>
                <div className="card-icon">{portfolio.total_profit_loss >= 0 ? '📈' : '📉'}</div>
                <div className="card-content">
                  <div className="card-label">Total P&L</div>
                  <div className="card-value">
                    {portfolio.total_profit_loss >= 0 ? '+' : ''}${portfolio.total_profit_loss.toLocaleString()}
                    <span className="card-percentage">
                      ({portfolio.total_profit_loss_percentage >= 0 ? '+' : ''}{portfolio.total_profit_loss_percentage}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="paper-trading-content">
          {/* Trading Form */}
          <div className="trading-panel">
            <h3>Execute Trade</h3>
            <form onSubmit={handleSubmit} className="paper-trade-form">
              <div className="trade-type-selector">
                <button
                  type="button"
                  className={`type-btn ${formData.trade_type === 'buy' ? 'active buy' : ''}`}
                  onClick={() => setFormData({ ...formData, trade_type: 'buy' })}
                >
                  📈 BUY
                </button>
                <button
                  type="button"
                  className={`type-btn ${formData.trade_type === 'sell' ? 'active sell' : ''}`}
                  onClick={() => setFormData({ ...formData, trade_type: 'sell' })}
                >
                  📉 SELL
                </button>
              </div>

              <div className="form-group">
                <label>Stock Symbol</label>
                <input
                  type="text"
                  placeholder="e.g., AAPL, TSLA, GOOGL"
                  value={formData.symbol}
                  onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Quantity</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  placeholder="Number of shares"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Notes (Optional)</label>
                <input
                  type="text"
                  placeholder="Trade notes..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                className={`execute-button ${formData.trade_type}`}
                disabled={loading}
              >
                {loading ? '⏳ Executing...' : `🚀 Execute ${formData.trade_type.toUpperCase()}`}
              </button>
            </form>

            {portfolio && (
              <div className="trading-info">
                <div className="info-item">
                  <span>Available Cash:</span>
                  <strong>${portfolio.total_cash.toLocaleString()}</strong>
                </div>
                <div className="info-item">
                  <span>Total Trades:</span>
                  <strong>{portfolio.num_trades}</strong>
                </div>
              </div>
            )}
          </div>

          {/* Holdings */}
          <div className="holdings-panel">
            <h3>Current Holdings</h3>
            {portfolio && Object.keys(portfolio.holdings).length > 0 ? (
              <div className="holdings-list">
                {Object.entries(portfolio.holdings).map(([symbol, data]) => (
                  <div key={symbol} className="holding-card">
                    <div className="holding-header">
                      <span className="holding-symbol">{symbol}</span>
                      <span className={`holding-pl ${data.profit_loss >= 0 ? 'profit' : 'loss'}`}>
                        {data.profit_loss >= 0 ? '+' : ''}${data.profit_loss}
                      </span>
                    </div>
                    <div className="holding-details">
                      <div className="detail-row">
                        <span>Quantity:</span>
                        <strong>{data.quantity}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Avg Price:</span>
                        <strong>${data.avg_price}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Current:</span>
                        <strong>${data.current_price}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Value:</span>
                        <strong>${data.current_value.toLocaleString()}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Return:</span>
                        <strong className={data.profit_loss_percentage >= 0 ? 'profit' : 'loss'}>
                          {data.profit_loss_percentage >= 0 ? '+' : ''}{data.profit_loss_percentage}%
                        </strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-holdings">
                <p>📭 No holdings yet</p>
                <p>Start by executing your first trade!</p>
              </div>
            )}
          </div>
        </div>

        {/* Trade History */}
        {trades.length > 0 && (
          <div className="trade-history-panel">
            <h3>📋 Recent Trades</h3>
            <div className="trades-list">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total Value</th>
                    <th>Cash After</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.id}>
                      <td>{new Date(trade.trade_date).toLocaleString()}</td>
                      <td><strong>{trade.symbol}</strong></td>
                      <td>
                        <span className={`trade-badge ${trade.trade_type}`}>
                          {trade.trade_type.toUpperCase()}
                        </span>
                      </td>
                      <td>{trade.quantity}</td>
                      <td>${trade.price}</td>
                      <td>${(trade.quantity * trade.price).toLocaleString()}</td>
                      <td>${trade.virtual_cash.toLocaleString()}</td>
                      <td className="notes">{trade.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Info Banner */}
        <div className="paper-info-banner">
          ℹ️ <strong>Paper Trading</strong> uses real-time market prices but virtual money.
          Perfect for testing strategies without financial risk!
        </div>
      </div>
    </>
  );
}

export default PaperTrading;