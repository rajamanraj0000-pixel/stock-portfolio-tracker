import React from 'react';
import TechnicalIndicators from '../components/TechnicalIndicators';

function IndicatorsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📈 Technical Indicators</h1>
        <p>Analyze stocks with RSI, MACD, and Moving Averages</p>
      </div>
      <TechnicalIndicators />
    </div>
  );
}

export default IndicatorsPage;