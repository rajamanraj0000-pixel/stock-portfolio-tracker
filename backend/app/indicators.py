import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_sma(symbol: str, period: int = 20, data_period: str = "3mo") -> Dict:
    """Calculate Simple Moving Average"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=data_period)
        
        if hist.empty or len(hist) < period:
            return {"error": "Insufficient data"}
        
        sma = hist['Close'].rolling(window=period).mean()
        current_price = hist['Close'].iloc[-1]
        current_sma = sma.iloc[-1]
        
        return {
            "sma": round(current_sma, 2),
            "current_price": round(current_price, 2),
            "signal": "BUY" if current_price > current_sma else "SELL",
            "difference": round(((current_price - current_sma) / current_sma) * 100, 2)
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_ema(symbol: str, period: int = 20, data_period: str = "3mo") -> Dict:
    """Calculate Exponential Moving Average"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=data_period)
        
        if hist.empty or len(hist) < period:
            return {"error": "Insufficient data"}
        
        ema = hist['Close'].ewm(span=period, adjust=False).mean()
        current_price = hist['Close'].iloc[-1]
        current_ema = ema.iloc[-1]
        
        return {
            "ema": round(current_ema, 2),
            "current_price": round(current_price, 2),
            "signal": "BUY" if current_price > current_ema else "SELL",
            "difference": round(((current_price - current_ema) / current_ema) * 100, 2)
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_rsi(symbol: str, period: int = 14, data_period: str = "3mo") -> Dict:
    """Calculate Relative Strength Index"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=data_period)
        
        if hist.empty or len(hist) < period + 1:
            return {"error": "Insufficient data"}
        
        # Calculate price changes
        delta = hist['Close'].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Determine signal
        if current_rsi > 70:
            signal = "OVERBOUGHT"
            recommendation = "SELL"
        elif current_rsi < 30:
            signal = "OVERSOLD"
            recommendation = "BUY"
        else:
            signal = "NEUTRAL"
            recommendation = "HOLD"
        
        return {
            "rsi": round(current_rsi, 2),
            "signal": signal,
            "recommendation": recommendation,
            "interpretation": {
                "overbought": "> 70",
                "oversold": "< 30",
                "neutral": "30-70"
            }
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_macd(symbol: str, data_period: str = "6mo") -> Dict:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=data_period)
        
        if hist.empty or len(hist) < 26:
            return {"error": "Insufficient data"}
        
        # Calculate MACD components
        ema_12 = hist['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = histogram.iloc[-1]
        
        # Determine signal
        if current_macd > current_signal and current_histogram > 0:
            signal = "BULLISH"
            recommendation = "BUY"
        elif current_macd < current_signal and current_histogram < 0:
            signal = "BEARISH"
            recommendation = "SELL"
        else:
            signal = "NEUTRAL"
            recommendation = "HOLD"
        
        return {
            "macd": round(current_macd, 2),
            "signal_line": round(current_signal, 2),
            "histogram": round(current_histogram, 2),
            "signal": signal,
            "recommendation": recommendation
        }
    except Exception as e:
        return {"error": str(e)}

def get_all_indicators(symbol: str) -> Dict:
    """Get all technical indicators for a symbol"""
    return {
        "symbol": symbol,
        "sma_20": calculate_sma(symbol, period=20),
        "sma_50": calculate_sma(symbol, period=50, data_period="6mo"),
        "ema_20": calculate_ema(symbol, period=20),
        "rsi": calculate_rsi(symbol),
        "macd": calculate_macd(symbol)
    }