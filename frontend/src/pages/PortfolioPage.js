import React, { useState, useEffect } from 'react';
import PortfolioStats from '../components/PortfolioStats';
import PortfolioChart from '../components/PortfolioChart';
import AddTransaction from '../components/AddTransaction';
import { api } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

function PortfolioPage() {
  const [portfolioId, setPortfolioId] = useState(null);
  const [stats, setStats] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserPortfolio();
  }, [refreshKey]);

  const fetchUserPortfolio = async () => {
    try {
      setLoading(true);
      const response = await api.getPortfolios();
      
      if (response.data.length > 0) {
        const userPortfolio = response.data[0];
        setPortfolioId(userPortfolio.id);
        
        const statsResponse = await api.getPortfolioStats(userPortfolio.id);
        setStats(statsResponse.data);
      } else {
        // Create portfolio if doesn't exist
        const newPortfolio = await api.createPortfolio({ name: "My Portfolio" });
        setPortfolioId(newPortfolio.data.id);
        
        const statsResponse = await api.getPortfolioStats(newPortfolio.data.id);
        setStats(statsResponse.data);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  const handleTransactionAdded = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (loading) return <LoadingSpinner message="Loading portfolio..." />;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>💼 Portfolio</h1>
        <p>Manage your holdings and transactions</p>
      </div>

      {portfolioId ? (
        <>
          <AddTransaction 
            portfolioId={portfolioId} 
            onTransactionAdded={handleTransactionAdded} 
          />
          <PortfolioStats key={refreshKey} portfolioId={portfolioId} />
          {stats && <PortfolioChart stats={stats} />}
        </>
      ) : (
        <div className="empty-state">
          <p>Creating your portfolio...</p>
        </div>
      )}
    </div>
  );
}

export default PortfolioPage;