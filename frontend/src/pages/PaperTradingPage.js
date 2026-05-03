import React from 'react';
import PaperTrading from '../components/PaperTrading';

function PaperTradingPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>💰 Paper Trading</h1>
        <p>Practice trading with virtual money</p>
      </div>
      <PaperTrading />
    </div>
  );
}

export default PaperTradingPage;