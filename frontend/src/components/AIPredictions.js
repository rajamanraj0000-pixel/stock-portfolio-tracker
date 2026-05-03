import React, { useState } from 'react';
import { api } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import Toast from './Toast';

function AIPredictions() {
  const [symbol, setSymbol] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const [predictionType, setPredictionType] = useState('lstm');

  const fetchPrediction = async (e) => {
    e.preventDefault();
    
    if (!symbol.trim()) { 
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return; 
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      let response = predictionType === 'quick' 
        ? await api.getQuickPrediction(symbol.toUpperCase()) 
        : await api.getLSTMPrediction(symbol.toUpperCase());
      
      if (response.data.prediction_available) {
        setPrediction(response.data);
        setToast({ message: 'Prediction generated successfully!', type: 'success' });
      } else {
        setError(response.data.error || 'Prediction not available');
        setToast({ message: 'Unable to generate prediction', type: 'error' });
      }
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching prediction');
      setToast({ message: 'Failed to generate prediction', type: 'error' });
      setLoading(false);
    }
  };

  const getPredictionClass = (prediction) => 
    prediction === 'BULLISH' ? 'prediction-bullish' : 'prediction-bearish';

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="ai-predictions">
        <h2>🤖 AI-Powered Price Predictions</h2>
        
        <form onSubmit={fetchPrediction} className="prediction-search">
          <input
            type="text"
            placeholder="Enter Stock Symbol (e.g., AAPL)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="symbol-input"
            disabled={loading}
          />
          <select 
            value={predictionType} 
            onChange={(e) => setPredictionType(e.target.value)} 
            className="prediction-type-select"
            disabled={loading}
          >
            <option value="lstm">LSTM Neural Network (30 days)</option>
            <option value="quick">Quick Trend Analysis (7 days)</option>
          </select>
          <button type="submit" className="predict-button" disabled={loading}>
            {loading ? '🔮 Predicting...' : '🔮 Predict'}
          </button>
        </form>

        {loading && (
          <div className="prediction-loading">
            <LoadingSpinner message={
              predictionType === 'lstm' 
                ? 'Training AI model... This may take 30-60 seconds' 
                : 'Analyzing trends...'
            } />
            <p className="loading-note">
              {predictionType === 'lstm' && '⚡ LSTM model training in progress'}
            </p>
          </div>
        )}

        {error && !loading && (
          <div className="error-state">
            <p>❌ {error}</p>
            <button onClick={(e) => fetchPrediction(e)} className="retry-button">
              🔄 Try Again
            </button>
          </div>
        )}

        {prediction && !loading && prediction.prediction_available && (
          <div className="prediction-results">
            <div className="prediction-header">
              <h3>{prediction.symbol} Price Forecast</h3>
              <span className="model-badge">{prediction.model}</span>
            </div>

            <div className={`prediction-card ${getPredictionClass(prediction.prediction)}`}>
              <div className="prediction-main">
                <div className="prediction-current">
                  <span className="label">Current Price</span>
                  <span className="price">${prediction.current_price}</span>
                </div>
                <div className="prediction-arrow">→</div>
                <div className="prediction-future">
                  <span className="label">Predicted ({prediction.prediction_days} days)</span>
                  <span className="price">${prediction.predicted_price}</span>
                </div>
              </div>

              <div className="prediction-change">
                <div className="change-amount">
                  {prediction.price_change >= 0 ? '+' : ''}${prediction.price_change}
                </div>
                <div className="change-percentage">
                  ({prediction.price_change_percentage >= 0 ? '+' : ''}{prediction.price_change_percentage}%)
                </div>
              </div>

              <div className="prediction-signal">
                {prediction.prediction === 'BULLISH' ? '📈' : '📉'} {prediction.prediction}
              </div>
            </div>

            {prediction.predictions && (
              <div className="prediction-timeline">
                <h4>Price Forecast Timeline</h4>
                <div className="timeline-container">
                  {prediction.predictions.map((pred, idx) => (
                    <div key={idx} className="timeline-item">
                      <span className="timeline-date">{pred.date}</span>
                      <span className="timeline-price">${pred.price}</span>
                      <div className="timeline-bar">
                        <div 
                          className="timeline-bar-fill" 
                          style={{
                            width: `${((pred.price - prediction.current_price) / prediction.current_price * 100 + 50)}%`,
                            background: pred.price >= prediction.current_price ? '#16a34a' : '#dc2626'
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="prediction-info">
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Confidence</span>
                  <span className="info-value">{prediction.confidence || 'Medium'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Model Type</span>
                  <span className="info-value">{prediction.model}</span>
                </div>
                {prediction.training_data_points && (
                  <div className="info-item">
                    <span className="info-label">Training Data Points</span>
                    <span className="info-value">{prediction.training_data_points}</span>
                  </div>
                )}
              </div>
              {prediction.note && (
                <div className="prediction-note">
                  ℹ️ {prediction.note}
                </div>
              )}
            </div>

            <div className="prediction-disclaimer">
              <strong>⚠️ Disclaimer:</strong> These predictions are generated by AI/ML models 
              and should not be considered as financial advice. Always do your own research 
              before making investment decisions. Past performance does not guarantee future results.
            </div>
          </div>
        )}

        {!prediction && !loading && !error && (
          <div className="empty-state">
            <p>🤖 AI Prediction Engine Ready</p>
            <p>Enter a stock symbol above to generate price forecasts</p>
          </div>
        )}
      </div>
    </>
  );
}

export default AIPredictions;