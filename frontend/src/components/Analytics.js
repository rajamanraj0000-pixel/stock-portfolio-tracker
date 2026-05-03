import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import Toast from './Toast';

function Analytics({ portfolioId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetchAnalytics();
},  [fetchAnalytics]);

  const fetchAnalytics = async () => {
    try {
      setError(null);
      setLoading(true);
      const response = await api.getAnalytics(portfolioId);
      setAnalytics(response.data);
      setLoading(false);
    } catch (e) { 
      console.error(e); 
      setError('Failed to load analytics');
      setToast({ message: 'Unable to fetch analytics', type: 'error' });
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading analytics..." />;
  
  if (error) {
    return (
      <div className="error-state">
        <p>❌ {error}</p>
        <button onClick={fetchAnalytics} className="retry-button">
          🔄 Retry
        </button>
      </div>
    );
  }
  
  if (!analytics) return null;

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="analytics-section">
        <div className="stats-header">
          <h2>Portfolio Analytics</h2>
          <button onClick={fetchAnalytics} className="refresh-button">🔄</button>
        </div>
        
        <div className="analytics-grid">
          <div className="analytics-card">
            <h3>Total Return</h3>
            <div className="analytics-value">{analytics.total_return}%</div>
          </div>
          <div className="analytics-card">
            <h3>CAGR</h3>
            <div className="analytics-value">{analytics.cagr}%</div>
          </div>
          <div className="analytics-card">
            <h3>XIRR</h3>
            <div className="analytics-value">{analytics.xirr}%</div>
          </div>
          <div className="analytics-card">
            <h3>Days Invested</h3>
            <div className="analytics-value">{analytics.days_invested}</div>
          </div>
        </div>

        {analytics.benchmark_comparison && (
          <div className="benchmark-section">
            <h3>Benchmark Comparison (S&P 500)</h3>
            <div className="benchmark-grid">
              <div className="benchmark-item">
                <span className="label">Benchmark Return:</span>
                <span className="value">{analytics.benchmark_comparison.benchmark_return}%</span>
              </div>
              <div className="benchmark-item">
                <span className="label">Alpha:</span>
                <span className={`value ${analytics.benchmark_comparison.alpha >= 0 ? 'profit' : 'loss'}`}>
                  {analytics.benchmark_comparison.alpha >= 0 ? '+' : ''}{analytics.benchmark_comparison.alpha}%
                </span>
              </div>
            </div>
          </div>
        )}
        
        {Object.keys(analytics.holdings_analytics).length > 0 ? (
          <div className="stock-analytics">
            <h3>Holdings Risk Metrics</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Volatility</th>
                    <th>Sharpe Ratio</th>
                    <th>Beta</th>
                    <th>Max Drawdown</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analytics.holdings_analytics).map(([symbol, data]) => (
                    <tr key={symbol}>
                      <td><strong>{symbol}</strong></td>
                      <td>{data.volatility}%</td>
                      <td className={data.sharpe_ratio >= 1 ? 'profit' : 'neutral'}>
                        {data.sharpe_ratio}
                      </td>
                      <td>{data.beta}</td>
                      <td className="loss">{data.max_drawdown}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <p>📊 No holdings data for analytics</p>
          </div>
        )}
      </div>
    </>
  );
}

export default Analytics;