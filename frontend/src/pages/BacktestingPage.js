import React from 'react';
import Backtesting from '../components/Backtesting';

function BacktestingPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>⚡ Strategy Backtesting</h1>
        <p>Test trading strategies on historical data</p>
      </div>
      <Backtesting />
    </div>
  );
}

export default BacktestingPage;