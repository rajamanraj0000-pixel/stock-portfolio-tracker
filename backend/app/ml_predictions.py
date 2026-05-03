import numpy as np
import pandas as pd
from .yf_helper import get_history
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except Exception:
    TENSORFLOW_AVAILABLE = False

def prepare_data(data, lookback=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    return np.array(X), np.array(y), scaler

def create_lstm_model(lookback=60):
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
    if not TENSORFLOW_AVAILABLE:
        return {"error": "TensorFlow not available", "prediction_available": False}
    try:
        hist = get_history(symbol, period="2y")
        if hist.empty or len(hist) < 100:
            return {"error": "Insufficient historical data", "prediction_available": False}

        current_price = float(hist['Close'].iloc[-1])
        close_prices = hist['Close'].values
        lookback = 60
        X, y, scaler = prepare_data(close_prices, lookback)

        if len(X) < 50:
            return {"error": "Not enough data for LSTM training", "prediction_available": False}

        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        split = int(0.8 * len(X))
        X_train, y_train = X[:split], y[:split]

        model = create_lstm_model(lookback)
        model.fit(X_train, y_train, epochs=10, batch_size=32,
                  verbose=0, validation_split=0.1)

        predictions = []
        last_sequence = close_prices[-lookback:]
        for _ in range(days_ahead):
            scaled_seq = scaler.transform(last_sequence.reshape(-1, 1))
            scaled_seq = scaled_seq.reshape(1, lookback, 1)
            pred_scaled = model.predict(scaled_seq, verbose=0)
            pred_price = float(scaler.inverse_transform(pred_scaled)[0][0])
            predictions.append(pred_price)
            last_sequence = np.append(last_sequence[1:], pred_price)

        predicted_price_30d = predictions[-1]
        price_change = predicted_price_30d - current_price
        price_change_pct = (price_change / current_price) * 100
        last_date = hist.index[-1]
        prediction_dates = [
            (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
            for i in range(days_ahead)
        ]

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price_30d, 2),
            "prediction_days": days_ahead,
            "price_change": round(price_change, 2),
            "price_change_percentage": round(price_change_pct, 2),
            "prediction": "BULLISH" if price_change > 0 else "BEARISH",
            "confidence": "Medium",
            "predictions": [
                {"date": prediction_dates[i], "price": round(predictions[i], 2)}
                for i in range(0, days_ahead, 5)
            ],
            "prediction_available": True,
            "model": "LSTM Neural Network",
            "training_data_points": len(close_prices)
        }
    except Exception as e:
        return {"error": str(e), "prediction_available": False}

def get_simple_trend_prediction(symbol: str, days_ahead: int = 30) -> Dict:
    try:
        hist = get_history(symbol, period="3mo")

        # Hard check — never proceed with empty data
        if hist is None or hist.empty:
            return {
                "error": f"No price data available for {symbol}",
                "prediction_available": False
            }

        current_price = float(hist['Close'].iloc[-1])
        sma_20 = float(hist['Close'].rolling(window=20).mean().iloc[-1])
        sma_50 = float(
            hist['Close'].rolling(window=50).mean().iloc[-1]
            if len(hist) >= 50 else sma_20
        )

        trend = (current_price - sma_50) / sma_50 * 100
        predicted_price = current_price * (1 + (trend / 100) * (days_ahead / 30))
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "prediction_days": days_ahead,
            "price_change": round(price_change, 2),
            "price_change_percentage": round(price_change_pct, 2),
            "prediction": "BULLISH" if price_change > 0 else "BEARISH",
            "confidence": "Low",
            "prediction_available": True,
            "model": "Trend Analysis",
            "note": "Simplified prediction based on moving averages"
        }
    except Exception as e:
        return {"error": str(e), "prediction_available": False}

def predict_stock(symbol: str, days_ahead: int = 30, use_lstm: bool = True) -> Dict:
    if use_lstm and TENSORFLOW_AVAILABLE:
        result = predict_stock_price_lstm(symbol, days_ahead)
        if not result.get("prediction_available", False):
            return get_simple_trend_prediction(symbol, days_ahead)
        return result
    return get_simple_trend_prediction(symbol, days_ahead)