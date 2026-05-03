from .yf_helper import get_ticker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

def backtest_strategy(
    symbol: str,
    strategy: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000,
    **kwargs
) -> Dict:
    """
    Backtest a trading strategy
    
    Strategies:
    - sma_crossover: Simple Moving Average Crossover
    - rsi_strategy: RSI Overbought/Oversold
    - buy_and_hold: Buy and Hold Benchmark
    """
    
    try:
        from .yf_helper import get_history_range
        hist = get_history_range(symbol, start_date, end_date)

        if hist is None or hist.empty:
            return {"error": f"No historical data for {symbol} in selected date range"}
        
        # Apply strategy with appropriate parameters
        if strategy == "sma_crossover":
            short_window = kwargs.get('short_window', 20)
            long_window = kwargs.get('long_window', 50)
            return backtest_sma_crossover(hist, initial_capital, short_window, long_window)
            
        elif strategy == "rsi_strategy":
            period = kwargs.get('period', 14)
            oversold = kwargs.get('oversold', 30)
            overbought = kwargs.get('overbought', 70)
            return backtest_rsi(hist, initial_capital, period, oversold, overbought)
            
        elif strategy == "buy_and_hold":
            return backtest_buy_and_hold(hist, initial_capital)
        else:
            return {"error": "Unknown strategy"}
            
    except Exception as e:
        return {"error": str(e)}

def backtest_sma_crossover(hist: pd.DataFrame, initial_capital: float, short_window: int = 20, long_window: int = 50) -> Dict:
    """Backtest Simple Moving Average Crossover Strategy"""
    
    # Calculate SMAs
    hist['SMA_Short'] = hist['Close'].rolling(window=short_window).mean()
    hist['SMA_Long'] = hist['Close'].rolling(window=long_window).mean()
    
    # Generate signals
    hist['Signal'] = 0
    hist.loc[hist['SMA_Short'] > hist['SMA_Long'], 'Signal'] = 1  # Buy
    hist.loc[hist['SMA_Short'] <= hist['SMA_Long'], 'Signal'] = -1  # Sell
    
    # Calculate positions
    hist['Position'] = hist['Signal'].diff()
    
    # Simulate trading
    capital = initial_capital
    shares = 0
    trades = []
    
    for index, row in hist.iterrows():
        if pd.isna(row['Position']):
            continue
            
        # Buy signal
        if row['Position'] == 2:  # Changed from -1 to 1 (crossover up)
            shares_to_buy = capital // row['Close']
            if shares_to_buy > 0:
                shares += shares_to_buy
                capital -= shares_to_buy * row['Close']
                trades.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'price': round(row['Close'], 2),
                    'shares': int(shares_to_buy),
                    'capital': round(capital, 2)
                })
        
        # Sell signal
        elif row['Position'] == -2:  # Changed from 1 to -1 (crossover down)
            if shares > 0:
                capital += shares * row['Close']
                trades.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'action': 'SELL',
                    'price': round(row['Close'], 2),
                    'shares': int(shares),
                    'capital': round(capital, 2)
                })
                shares = 0
    
    # Final portfolio value
    final_price = hist['Close'].iloc[-1]
    final_value = capital + (shares * final_price)
    
    # Calculate metrics
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    num_trades = len(trades)
    
    return {
        'strategy': f'SMA Crossover ({short_window}/{long_window})',
        'initial_capital': round(initial_capital, 2),
        'final_value': round(final_value, 2),
        'total_return': round(total_return, 2),
        'profit_loss': round(final_value - initial_capital, 2),
        'num_trades': num_trades,
        'trades': trades[-10:] if len(trades) > 10 else trades,  # Last 10 trades
        'total_trades': num_trades,
        'start_date': hist.index[0].strftime('%Y-%m-%d'),
        'end_date': hist.index[-1].strftime('%Y-%m-%d')
    }

def backtest_rsi(hist: pd.DataFrame, initial_capital: float, period: int = 14, oversold: int = 30, overbought: int = 70) -> Dict:
    """Backtest RSI Strategy"""
    
    # Calculate RSI
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    hist['RSI'] = 100 - (100 / (1 + rs))
    
    # Generate signals
    capital = initial_capital
    shares = 0
    trades = []
    position = None
    
    for index, row in hist.iterrows():
        if pd.isna(row['RSI']):
            continue
        
        # Buy when oversold
        if row['RSI'] < oversold and position != 'long':
            shares_to_buy = capital // row['Close']
            if shares_to_buy > 0:
                shares += shares_to_buy
                capital -= shares_to_buy * row['Close']
                position = 'long'
                trades.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'price': round(row['Close'], 2),
                    'shares': int(shares_to_buy),
                    'rsi': round(row['RSI'], 2),
                    'capital': round(capital, 2)
                })
        
        # Sell when overbought
        elif row['RSI'] > overbought and position == 'long' and shares > 0:
            capital += shares * row['Close']
            trades.append({
                'date': index.strftime('%Y-%m-%d'),
                'action': 'SELL',
                'price': round(row['Close'], 2),
                'shares': int(shares),
                'rsi': round(row['RSI'], 2),
                'capital': round(capital, 2)
            })
            shares = 0
            position = None
    
    # Final portfolio value
    final_price = hist['Close'].iloc[-1]
    final_value = capital + (shares * final_price)
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    return {
        'strategy': f'RSI Strategy (Period: {period}, Oversold: {oversold}, Overbought: {overbought})',
        'initial_capital': round(initial_capital, 2),
        'final_value': round(final_value, 2),
        'total_return': round(total_return, 2),
        'profit_loss': round(final_value - initial_capital, 2),
        'num_trades': len(trades),
        'trades': trades[-10:] if len(trades) > 10 else trades,
        'total_trades': len(trades),
        'start_date': hist.index[0].strftime('%Y-%m-%d'),
        'end_date': hist.index[-1].strftime('%Y-%m-%d')
    }

def backtest_buy_and_hold(hist: pd.DataFrame, initial_capital: float) -> Dict:
    """Backtest Buy and Hold Strategy (Benchmark)"""
    
    start_price = hist['Close'].iloc[0]
    end_price = hist['Close'].iloc[-1]
    
    shares = initial_capital / start_price
    final_value = shares * end_price
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    return {
        'strategy': 'Buy and Hold',
        'initial_capital': round(initial_capital, 2),
        'final_value': round(final_value, 2),
        'total_return': round(total_return, 2),
        'profit_loss': round(final_value - initial_capital, 2),
        'num_trades': 1,
        'trades': [{
            'date': hist.index[0].strftime('%Y-%m-%d'),
            'action': 'BUY',
            'price': round(start_price, 2),
            'shares': round(shares, 2),
            'capital': 0
        }],
        'total_trades': 1,
        'start_date': hist.index[0].strftime('%Y-%m-%d'),
        'end_date': hist.index[-1].strftime('%Y-%m-%d')
    }