import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats
import yfinance as yf
from typing import List, Dict
from .models import Transaction

def calculate_cagr(beginning_value: float, ending_value: float, num_years: float) -> float:
    """Calculate Compound Annual Growth Rate"""
    if beginning_value <= 0 or num_years <= 0:
        return 0.0
    
    cagr = (pow(ending_value / beginning_value, 1 / num_years) - 1) * 100
    return round(cagr, 2)

def calculate_xirr(transactions: List[Transaction], current_value: float) -> float:
    """Calculate XIRR (Extended Internal Rate of Return)"""
    if not transactions:
        return 0.0
    
    # Prepare cash flows
    cash_flows = []
    dates = []
    
    for txn in transactions:
        if txn.transaction_type == "buy":
            cash_flows.append(-txn.quantity * txn.price)  # Outflow
        else:
            cash_flows.append(txn.quantity * txn.price)   # Inflow
        dates.append(txn.transaction_date)
    
    # Add current value as final inflow
    cash_flows.append(current_value)
    dates.append(datetime.now())
    
    # Simple IRR calculation (approximation)
    try:
        total_invested = sum([cf for cf in cash_flows if cf < 0])
        total_returned = sum([cf for cf in cash_flows if cf > 0])
        
        if total_invested == 0:
            return 0.0
        
        days = (dates[-1] - dates[0]).days
        if days == 0:
            return 0.0
        
        years = days / 365.25
        roi = (total_returned / abs(total_invested) - 1) * 100
        annualized = (pow(1 + roi/100, 1/years) - 1) * 100 if years > 0 else roi
        
        return round(annualized, 2)
    except:
        return 0.0

def calculate_volatility(symbol: str, period: str = "1y") -> float:
    """Calculate stock volatility (standard deviation of returns)"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return 0.0
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252) * 100  # 252 trading days
        
        return round(volatility, 2)
    except:
        return 0.0

def calculate_sharpe_ratio(symbol: str, risk_free_rate: float = 2.0, period: str = "1y") -> float:
    """Calculate Sharpe Ratio"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return 0.0
        
        # Calculate returns
        returns = hist['Close'].pct_change().dropna()
        
        # Annualized return
        avg_return = returns.mean() * 252 * 100
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252) * 100
        
        if volatility == 0:
            return 0.0
        
        # Sharpe Ratio
        sharpe = (avg_return - risk_free_rate) / volatility
        
        return round(sharpe, 2)
    except:
        return 0.0

def calculate_beta(symbol: str, benchmark: str = "^GSPC", period: str = "1y") -> float:
    """Calculate Beta (correlation with market)"""
    try:
        stock = yf.Ticker(symbol)
        market = yf.Ticker(benchmark)
        
        stock_hist = stock.history(period=period)
        market_hist = market.history(period=period)
        
        if stock_hist.empty or market_hist.empty:
            return 1.0
        
        # Calculate returns
        stock_returns = stock_hist['Close'].pct_change().dropna()
        market_returns = market_hist['Close'].pct_change().dropna()
        
        # Align dates
        combined = pd.DataFrame({
            'stock': stock_returns,
            'market': market_returns
        }).dropna()
        
        if len(combined) < 2:
            return 1.0
        
        # Calculate beta using covariance
        covariance = combined['stock'].cov(combined['market'])
        market_variance = combined['market'].var()
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        
        return round(beta, 2)
    except:
        return 1.0

def calculate_max_drawdown(symbol: str, period: str = "1y") -> float:
    """Calculate Maximum Drawdown"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return 0.0
        
        # Calculate cumulative returns
        cumulative = (1 + hist['Close'].pct_change()).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max * 100
        
        max_drawdown = drawdown.min()
        
        return round(max_drawdown, 2)
    except:
        return 0.0

def compare_with_benchmark(portfolio_return: float, benchmark: str = "^GSPC", period: str = "1y") -> Dict:
    """Compare portfolio performance with benchmark"""
    try:
        market = yf.Ticker(benchmark)
        hist = market.history(period=period)
        
        if hist.empty:
            return {
                "benchmark_return": 0.0,
                "alpha": 0.0,
                "outperformance": portfolio_return
            }
        
        # Calculate benchmark return
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        benchmark_return = ((end_price - start_price) / start_price) * 100
        
        # Calculate alpha (excess return)
        alpha = portfolio_return - benchmark_return
        
        return {
            "benchmark_name": "S&P 500",
            "benchmark_return": round(benchmark_return, 2),
            "alpha": round(alpha, 2),
            "outperformance": round(alpha, 2)
        }
    except:
        return {
            "benchmark_return": 0.0,
            "alpha": 0.0,
            "outperformance": portfolio_return
        }

def get_portfolio_analytics(transactions: List[Transaction], current_stats: Dict) -> Dict:
    """Get comprehensive portfolio analytics"""
    
    if not transactions:
        return {
            "cagr": 0.0,
            "xirr": 0.0,
            "total_return": 0.0,
            "holdings_analytics": {},
            "benchmark_comparison": {}
        }
    
    # Calculate time period
    first_transaction = min(transactions, key=lambda x: x.transaction_date)
    days_invested = (datetime.now() - first_transaction.transaction_date).days
    years_invested = max(days_invested / 365.25, 0.01)  # Minimum 0.01 to avoid division by zero
    
    # Calculate CAGR
    total_invested = current_stats['total_investment']
    current_value = current_stats['current_value']
    cagr = calculate_cagr(total_invested, current_value, years_invested)
    
    # Calculate XIRR
    xirr = calculate_xirr(transactions, current_value)
    
    # Calculate total return
    total_return = current_stats['total_profit_loss_percentage']
    
    # Analytics for each holding
    holdings_analytics = {}
    for symbol, data in current_stats.get('holdings', {}).items():
        holdings_analytics[symbol] = {
            "volatility": calculate_volatility(symbol),
            "sharpe_ratio": calculate_sharpe_ratio(symbol),
            "beta": calculate_beta(symbol),
            "max_drawdown": calculate_max_drawdown(symbol)
        }
    
    # Benchmark comparison
    benchmark_comparison = compare_with_benchmark(total_return)
    
    return {
        "cagr": cagr,
        "xirr": xirr,
        "total_return": total_return,
        "years_invested": round(years_invested, 2),
        "days_invested": days_invested,
        "holdings_analytics": holdings_analytics,
        "benchmark_comparison": benchmark_comparison
    }