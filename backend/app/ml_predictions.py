import numpy as np
import pandas as pd
from .yf_helper import get_ticker, get_history
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except:
    TENSORFLOW_AVAILABLE = False

def prepare_data(data, lookback=60):
    """Prepare data for LSTM model"""
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    return np.array(X), np.array(y), scaler

def create_lstm_model(lookback=60):
    """Create LSTM neural network model"""
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=True),
        Dropout(0.2),
        LSTM(units=50),
        Dropout(0.2),
        Dense(units=1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def predict_stock_price_lstm(symbol: str, days_ahead: int = 30) -> Dict:
    """Predict future stock prices using LSTM"""
    
    if not TENSORFLOW_AVAILABLE:
        return {
            "error": "TensorFlow not installed. Install with: pip install tensorflow",
            "prediction_available": False
        }
    
    try:
        # Fetch historical data (2 years)
        hist = get_history(symbol, period="2y")
        if hist is None:
            hist = __import__('pandas').DataFrame()
        
        if hist.empty or len(hist) < 100:
            return {
                "error": "Insufficient historical data",
                "prediction_available": False
            }
        
        # Get current price
        current_price = hist['Close'].iloc[-1]
        
        # Prepare data
        close_prices = hist['Close'].values
        lookback = 60
        
        X, y, scaler = prepare_data(close_prices, lookback)
        
        if len(X) < 50:
            return {
                "error": "Not enough data for training",
                "prediction_available": False
            }
        
        # Reshape X for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split data (80% train, 20% test)
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Create and train model (with fewer epochs for speed)
        model = create_lstm_model(lookback)
        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0, validation_split=0.1)
        
        # Make predictions
        predictions = []
        last_sequence = close_prices[-lookback:]
        
        for _ in range(days_ahead):
            # Scale the sequence
            scaled_sequence = scaler.transform(last_sequence.reshape(-1, 1))
            scaled_sequence = scaled_sequence.reshape(1, lookback, 1)
            
            # Predict next value
            predicted_scaled = model.predict(scaled_sequence, verbose=0)
            predicted_price = scaler.inverse_transform(predicted_scaled)[0][0]
            
            predictions.append(predicted_price)
            
            # Update sequence for next prediction
            last_sequence = np.append(last_sequence[1:], predicted_price)
        
        # Calculate metrics
        predicted_price_30d = predictions[-1]
        price_change = predicted_price_30d - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Generate prediction dates
        last_date = hist.index[-1]
        prediction_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                           for i in range(days_ahead)]
        
        return {
            "symbol": symbol,
            "current_price": round(float(current_price), 2),
            "predicted_price": round(float(predicted_price_30d), 2),
            "prediction_days": days_ahead,
            "price_change": round(float(price_change), 2),
            "price_change_percentage": round(float(price_change_pct), 2),
            "prediction": "BULLISH" if price_change > 0 else "BEARISH",
            "confidence": "Medium",  # Simplified confidence
            "predictions": [
                {
                    "date": prediction_dates[i],
                    "price": round(float(predictions[i]), 2)
                }
                for i in range(0, days_ahead, 5)  # Every 5 days
            ],
            "prediction_available": True,
            "model": "LSTM Neural Network",
            "training_data_points": len(close_prices)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "prediction_available": False
        }

def get_simple_trend_prediction(symbol: str, days_ahead: int = 30) -> Dict:
    """Simple trend-based prediction (fallback if LSTM fails)"""
    try:
        hist = get_history(symbol, period="3mo")
        if hist is None:
            hist = __import__('pandas').DataFrame()
        
        if hist.empty:
            return {"error": "No data available"}
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate simple moving average trend
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else sma_20
        
        # Simple trend calculation
        trend = (current_price - sma_50) / sma_50 * 100
        
        # Predict based on trend
        predicted_price = current_price * (1 + (trend / 100) * (days_ahead / 30))
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        return {
            "symbol": symbol,
            "current_price": round(float(current_price), 2),
            "predicted_price": round(float(predicted_price), 2),
            "prediction_days": days_ahead,
            "price_change": round(float(price_change), 2),
            "price_change_percentage": round(float(price_change_pct), 2),
            "prediction": "BULLISH" if price_change > 0 else "BEARISH",
            "confidence": "Low",
            "prediction_available": True,
            "model": "Trend Analysis",
            "note": "Simplified prediction based on moving averages"
        }
    except Exception as e:
        return {"error": str(e), "prediction_available": False}

def predict_stock(symbol: str, days_ahead: int = 30, use_lstm: bool = True) -> Dict:
    """Main prediction function"""
    if use_lstm and TENSORFLOW_AVAILABLE:
        result = predict_stock_price_lstm(symbol, days_ahead)
        # If LSTM fails, fallback to simple prediction
        if not result.get("prediction_available", False):
            return get_simple_trend_prediction(symbol, days_ahead)
        return result
    else:
        return get_simple_trend_prediction(symbol, days_ahead)