import React from 'react';
import AIPredictions from '../components/AIPredictions';

function PredictionsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🤖 AI Predictions</h1>
        <p>Machine learning powered stock price forecasts</p>
      </div>
      <AIPredictions />
    </div>
  );
}

export default PredictionsPage;