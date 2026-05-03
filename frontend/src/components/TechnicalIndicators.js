import React, { useState } from 'react';
import { api } from '../services/api';
import Toast from './Toast';

function TechnicalIndicators() {
  const [symbol, setSymbol] = useState('');
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  const fetchIndicators = async (e) => {
    e.preventDefault();

    if (!symbol.trim()) {
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.getIndicators(symbol.toUpperCase());
      setIndicators(response.data);
      setToast({ message: 'Indicators loaded successfully!', type: 'success' });
    } catch (err) {
      setError('Error fetching indicators. Please try again.');
      setToast({ message: 'Failed to load indicators', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getSignalClass = (signal) => {
    if (signal === 'BUY' || signal === 'BULLISH') return 'signal-buy';
    if (signal === 'SELL' || signal === 'BEARISH') return 'signal-sell';
    return 'signal-neutral';
  };

  const getRSIClass = (rsi) => {
    if (rsi > 70) return 'rsi-overbought';
    if (rsi < 30) return 'rsi-oversold';
    return 'rsi-neutral';
  };

  return (
    <>
      {/* ✅ Toast FIXED (inside component) */}
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}

      <div className="technical-indicators">
        <h2>📈 Technical Indicators</h2>

        {/* Search Form */}
        <form onSubmit={fetchIndicators} className="indicator-search">
          <input
            type="text"
            placeholder="Enter Stock Symbol (e.g., AAPL)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="symbol-input"
          />
          <button type="submit" className="search-button">
            Analyze
          </button>
        </form>

        {loading && <div className="loading">Analyzing {symbol}...</div>}
        {error && <div className="error">{error}</div>}

        {/* Indicators Display */}
        {indicators && !loading && (
          <div className="indicators-results">
            <h3>Analysis for {indicators.symbol}</h3>
            <p className="current-price">
              Current Price: ${indicators.sma_20?.current_price}
            </p>

            {/* Moving Averages */}
            <div className="indicator-section">
              <h4>Moving Averages</h4>
              <div className="indicator-grid">

                {/* SMA 20 */}
                <div className="indicator-card">
                  <div className="indicator-header">
                    <span className="indicator-name">SMA (20)</span>
                    <span className={`signal-badge ${getSignalClass(indicators.sma_20?.signal)}`}>
                      {indicators.sma_20?.signal}
                    </span>
                  </div>
                  <div className="indicator-value">${indicators.sma_20?.sma}</div>
                  <div className="indicator-detail">
                    Difference: {indicators.sma_20?.difference > 0 ? '+' : ''}
                    {indicators.sma_20?.difference}%
                  </div>
                </div>

                {/* SMA 50 */}
                <div className="indicator-card">
                  <div className="indicator-header">
                    <span className="indicator-name">SMA (50)</span>
                    <span className={`signal-badge ${getSignalClass(indicators.sma_50?.signal)}`}>
                      {indicators.sma_50?.signal}
                    </span>
                  </div>
                  <div className="indicator-value">${indicators.sma_50?.sma}</div>
                  <div className="indicator-detail">
                    Difference: {indicators.sma_50?.difference > 0 ? '+' : ''}
                    {indicators.sma_50?.difference}%
                  </div>
                </div>

                {/* EMA 20 */}
                <div className="indicator-card">
                  <div className="indicator-header">
                    <span className="indicator-name">EMA (20)</span>
                    <span className={`signal-badge ${getSignalClass(indicators.ema_20?.signal)}`}>
                      {indicators.ema_20?.signal}
                    </span>
                  </div>
                  <div className="indicator-value">${indicators.ema_20?.ema}</div>
                  <div className="indicator-detail">
                    Difference: {indicators.ema_20?.difference > 0 ? '+' : ''}
                    {indicators.ema_20?.difference}%
                  </div>
                </div>

              </div>
            </div>

            {/* RSI */}
            <div className="indicator-section">
              <h4>Relative Strength Index (RSI)</h4>
              <div className="rsi-container">
                <div className={`rsi-gauge ${getRSIClass(indicators.rsi?.rsi)}`}>
                  <div className="rsi-value">{indicators.rsi?.rsi}</div>
                  <div className="rsi-label">{indicators.rsi?.signal}</div>
                </div>
              </div>
            </div>

            {/* MACD */}
            <div className="indicator-section">
              <h4>MACD</h4>
              <div className="macd-container">
                <div className="macd-values">
                  <div className="macd-item">
                    <span>MACD:</span>
                    <span>{indicators.macd?.macd}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </>
  );
}

export default TechnicalIndicators;