import React, { useState, useEffect } from 'react';
import Analytics from '../components/Analytics';
import { api } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

function AnalyticsPage() {
  const [portfolioId, setPortfolioId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserPortfolio();
  }, []);

  const fetchUserPortfolio = async () => {
    try {
      const response = await api.getPortfolios();
      
      if (response.data.length > 0) {
        setPortfolioId(response.data[0].id);
      } else {
        const newPortfolio = await api.createPortfolio({ name: "My Portfolio" });
        setPortfolioId(newPortfolio.data.id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading analytics..." />;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📊 Portfolio Analytics</h1>
        <p>Deep insights into your portfolio performance</p>
      </div>

      {portfolioId && <Analytics portfolioId={portfolioId} />}
    </div>
  );
}

export default AnalyticsPage;