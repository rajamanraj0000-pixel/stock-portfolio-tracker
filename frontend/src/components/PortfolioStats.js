import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import Toast from './Toast';

function PortfolioStats({ portfolioId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchStats();
},  [fetchStats]);

  const fetchStats = async () => {
    try {
      setError(null);
      const response = await api.getPortfolioStats(portfolioId);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setError(error.response?.data?.detail || 'Failed to load portfolio stats');
      setToast({ 
        message: 'Unable to fetch portfolio data', 
        type: 'error' 
      });
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading portfolio stats..." />;
  
  if (error) {
    return (
      <div className="error-state">
        <p>❌ {error}</p>
        <button onClick={fetchStats} className="retry-button">
          🔄 Retry
        </button>
      </div>
    );
  }
  
  if (!stats) {
    return (
      <div className="empty-state">
        <p>📭 No portfolio data available</p>
        <p>Add your first transaction to get started!</p>
      </div>
    );
  }

  const isProfit = stats.total_profit_loss >= 0;

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="portfolio-stats">
        <div className="stats-header">
          <h2>Portfolio Overview</h2>
          <button onClick={fetchStats} className="refresh-button" title="Refresh data">
            🔄
          </button>
        </div>
        
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Investment</h3>
            <p className="stat-value">${stats.total_investment.toFixed(2)}</p>
          </div>
          
          <div className="stat-card">
            <h3>Current Value</h3>
            <p className="stat-value">${stats.current_value.toFixed(2)}</p>
          </div>
          
          <div className="stat-card">
            <h3>Total P&L</h3>
            <p className={`stat-value ${isProfit ? 'profit' : 'loss'}`}>
              {isProfit ? '+' : ''}${stats.total_profit_loss.toFixed(2)} 
              ({isProfit ? '+' : ''}{stats.total_profit_loss_percentage.toFixed(2)}%)
            </p>
          </div>
        </div>

        {Object.keys(stats.holdings).length > 0 ? (
          <div className="holdings">
            <h3>Holdings</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Avg Price</th>
                    <th>Current Price</th>
                    <th>Invested</th>
                    <th>Current Value</th>
                    <th>P&L</th>
                    <th>P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(stats.holdings).map(([symbol, data]) => (
                    <tr key={symbol}>
                      <td><strong>{symbol}</strong></td>
                      <td>{data.quantity}</td>
                      <td>${data.avg_price}</td>
                      <td>${data.current_price}</td>
                      <td>${data.invested}</td>
                      <td>${data.current_value}</td>
                      <td className={data.profit_loss >= 0 ? 'profit' : 'loss'}>
                        {data.profit_loss >= 0 ? '+' : ''}${data.profit_loss}
                      </td>
                      <td className={data.profit_loss >= 0 ? 'profit' : 'loss'}>
                        {data.profit_loss_percentage >= 0 ? '+' : ''}{data.profit_loss_percentage}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <p>📊 No holdings yet</p>
            <p>Buy some stocks to see them here</p>
          </div>
        )}
      </div>
    </>
  );
}

export default PortfolioStats;