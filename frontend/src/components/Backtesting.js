import React, { useState } from 'react';
import { api } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import Toast from './Toast';

function Backtesting() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const [formData, setFormData] = useState({
    symbol: '',
    strategy: 'sma_crossover',
    start_date: '2023-01-01',
    end_date: '2024-12-31',
    initial_capital: 10000
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.symbol.trim()) {
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return;
    }

    if (parseFloat(formData.initial_capital) <= 0) {
      setToast({ message: 'Initial capital must be greater than 0', type: 'error' });
      return;
    }

    if (new Date(formData.start_date) >= new Date(formData.end_date)) {
      setToast({ message: 'Start date must be before end date', type: 'error' });
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.runBacktest(formData);
      
      if (response.data.error) {
        setError(response.data.error);
        setToast({ message: 'Backtest failed', type: 'error' });
      } else {
        setResult(response.data);
        setToast({ message: 'Backtest completed successfully!', type: 'success' });
      }
      setLoading(false);
    } catch (e) {
      setError(e.response?.data?.detail || 'Backtest failed');
      setToast({ message: 'Failed to run backtest', type: 'error' });
      setLoading(false);
    }
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="backtesting-section">
        <h2>📈 Strategy Backtesting</h2>
        <p className="section-description">
          Test trading strategies on historical data to evaluate performance
        </p>

        <div className="backtest-form-container">
          <h3>Configure Backtest</h3>
          <form onSubmit={handleSubmit} className="backtest-form">
            <div className="form-row">
              <div className="form-group">
                <label>Stock Symbol</label>
                <input
                  type="text"
                  placeholder="e.g., AAPL"
                  value={formData.symbol}
                  onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Strategy</label>
                <select
                  value={formData.strategy}
                  onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
                  disabled={loading}
                >
                  <option value="sma_crossover">SMA Crossover (20/50)</option>
                  <option value="rsi_strategy">RSI Strategy</option>
                  <option value="buy_and_hold">Buy and Hold</option>
                </select>
              </div>

              <div className="form-group">
                <label>Initial Capital ($)</label>
                <input
                  type="number"
                  step="100"
                  min="100"
                  value={formData.initial_capital}
                  onChange={(e) => setFormData({ ...formData, initial_capital: e.target.value })}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" className="backtest-button" disabled={loading}>
              {loading ? '⏳ Running Backtest...' : '🚀 Run Backtest'}
            </button>
          </form>
        </div>

        {loading && (
          <LoadingSpinner message="Running backtest simulation..." />
        )}

        {error && !loading && (
          <div className="error-state">
            <p>❌ {error}</p>
            <button onClick={handleSubmit} className="retry-button">
              🔄 Try Again
            </button>
          </div>
        )}

        {result && !loading && (
          <div className="backtest-results">
            <h3>Backtest Results: {result.strategy}</h3>

            <div className="results-summary">
              <div className="summary-card">
                <div className="card-label">Initial Capital</div>
                <div className="card-value">${result.initial_capital.toLocaleString()}</div>
              </div>

              <div className="summary-card">
                <div className="card-label">Final Value</div>
                <div className="card-value">${result.final_value.toLocaleString()}</div>
              </div>

              <div className="summary-card">
                <div className="card-label">Total Trades</div>
                <div className="card-value">{result.num_trades}</div>
              </div>

              <div className="summary-card">
                <div className="card-label">Period</div>
                <div className="card-value">
                  {result.start_date} to {result.end_date}
                </div>
              </div>
            </div>

            <div className="performance-metrics">
              <div className={`metric-card ${result.total_return >= 0 ? 'positive' : 'negative'}`}>
                <div className="metric-icon">
                  {result.total_return >= 0 ? '📈' : '📉'}
                </div>
                <div className="metric-content">
                  <div className="metric-label">Total Return</div>
                  <div className="metric-value">
                    {result.total_return >= 0 ? '+' : ''}{result.total_return}%
                  </div>
                </div>
              </div>

              <div className={`metric-card ${result.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                <div className="metric-icon">💰</div>
                <div className="metric-content">
                  <div className="metric-label">Profit/Loss</div>
                  <div className="metric-value">
                    {result.profit_loss >= 0 ? '+' : ''}${result.profit_loss.toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="metric-card neutral">
                <div className="metric-icon">📊</div>
                <div className="metric-content">
                  <div className="metric-label">Number of Trades</div>
                  <div className="metric-value">{result.num_trades}</div>
                </div>
              </div>
            </div>

            {result.trades && result.trades.length > 0 && (
              <div className="trade-history">
                <h4>Recent Trades ({result.total_trades} total)</h4>
                <div className="trades-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Action</th>
                        <th>Price</th>
                        <th>Shares</th>
                        <th>Capital</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.trades.map((trade, idx) => (
                        <tr key={idx}>
                          <td>{trade.date}</td>
                          <td>
                            <span className={`trade-action ${trade.action.toLowerCase()}`}>
                              {trade.action}
                            </span>
                          </td>
                          <td>${trade.price}</td>
                          <td>{trade.shares}</td>
                          <td>${trade.capital.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="backtest-disclaimer">
              <strong>⚠️ Important:</strong> Past performance is not indicative of future results. 
              Backtesting results do not account for transaction costs, slippage, or market impact. 
              Use these results for educational purposes only.
            </div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="empty-state">
            <p>📊 Ready to Backtest</p>
            <p>Configure your strategy above and click "Run Backtest"</p>
          </div>
        )}
      </div>
    </>
  );
}

export default Backtesting;