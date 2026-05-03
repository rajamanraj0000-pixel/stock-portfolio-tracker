import React, { useState, useEffect } from 'react';
import PortfolioStats from '../components/PortfolioStats';
import Watchlist from '../components/Watchlist';
import { api } from '../services/api';
import StockChart from '../components/StockChart';
import LoadingSpinner from '../components/LoadingSpinner';

function DashboardPage() {
  const [portfolioId, setPortfolioId] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchUserPortfolio();
  }, []);

  const fetchUserPortfolio = async () => {
    try {
      setLoading(true);
      
      // Get user's portfolios
      const response = await api.getPortfolios();
      
      if (response.data.length > 0) {
        // Use the first portfolio (or latest)
        const userPortfolio = response.data[0];
        setPortfolioId(userPortfolio.id);
        
        // Fetch stats for this portfolio
        const statsResponse = await api.getPortfolioStats(userPortfolio.id);
        setStats(statsResponse.data);
      } else {
        // No portfolio exists, create one
        const newPortfolio = await api.createPortfolio({ name: "My Portfolio" });
        setPortfolioId(newPortfolio.data.id);
        
        // Fetch stats for new portfolio
        const statsResponse = await api.getPortfolioStats(newPortfolio.data.id);
        setStats(statsResponse.data);
      }
      
      setLoading(false);
    } catch (err) {
      console.error("Error fetching portfolio:", err);
      setError("Failed to load portfolio data");
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading your portfolio..." />;
  if (error) return <div className="error-state">{error}</div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p>Portfolio Overview</p>
      </div>

      {portfolioId ? (
        <>
          <div className="card">
            <PortfolioStats portfolioId={portfolioId} />
            <StockChart symbol="AAPL" />
          </div>

          {stats && (
            <div className="dashboard-cards">
              <div className="card stat-card">
                <p>Total Investment</p>
                <h2>₹{stats.total_investment?.toLocaleString() || 0}</h2>
              </div>

              <div className="card stat-card">
                <p>Current Value</p>
                <h2>₹{stats.current_value?.toLocaleString() || 0}</h2>
              </div>

              <div className={`card stat-card ${stats.total_profit_loss >= 0 ? 'profit' : 'loss'}`}>
                <p>Profit/Loss</p>
                <h2>
                  {stats.total_profit_loss >= 0 ? '+' : ''}₹
                  {Math.abs(stats.total_profit_loss || 0).toLocaleString()}
                </h2>
              </div>

              <div className={`card stat-card ${stats.total_profit_loss_percentage >= 0 ? 'profit' : 'loss'}`}>
                <p>Return %</p>
                <h2>
                  {stats.total_profit_loss_percentage >= 0 ? '+' : ''}
                  {Math.abs(stats.total_profit_loss_percentage || 0).toFixed(2)}%
                </h2>
              </div>
            </div>
          )}

          <Watchlist />
        </>
      ) : (
        <div className="empty-state">
          <p>📭 No portfolio found</p>
          <p>Creating your portfolio...</p>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;