import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';  // NEW
import PortfolioStats from './PortfolioStats';
import AddTransaction from './AddTransaction';
import Analytics from './Analytics';
import TechnicalIndicators from './TechnicalIndicators';
import AIPredictions from './AIPredictions';
import Alerts from './Alerts';
import Backtesting from './Backtesting';
import PaperTrading from './PaperTrading';
import { api } from '../services/api';

function Dashboard() {
  const [portfolioId, setPortfolioId] = useState(6);
  const [refreshKey, setRefreshKey] = useState(0);
  const [portfolios, setPortfolios] = useState([]);

  useEffect(() => {
    api.getPortfolios()
      .then(response => {
        console.log('Available portfolios:', response.data);
        setPortfolios(response.data);
        if (response.data.length > 0) {
          setPortfolioId(response.data[response.data.length - 1].id);
        }
      })
      .catch(error => {
        console.error('Error fetching portfolios:', error);
      });
  }, []);

  const handleTransactionAdded = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <>
      <Navbar />  {/* NEW */}
      <div className="dashboard">
        <h1>📊 Portfolio Dashboard</h1>
        
        {portfolios.length > 0 && (
          <div style={{textAlign: 'center', marginBottom: '20px', color: '#666'}}>
            Portfolio ID: {portfolioId}
          </div>
        )}
        
        <AddTransaction 
          portfolioId={portfolioId} 
          onTransactionAdded={handleTransactionAdded}
        />
        
        <PortfolioStats key={refreshKey} portfolioId={portfolioId} />
        
        <Analytics key={refreshKey} portfolioId={portfolioId} />
        
        <TechnicalIndicators />
        
        <AIPredictions />
        
        <Alerts />
        
        <Backtesting />
        
        <PaperTrading />
      </div>
    </>
  );
}

export default Dashboard;