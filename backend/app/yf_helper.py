import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_ticker(symbol: str):
    """Get yfinance ticker with headers to avoid Yahoo Finance blocking"""
    session = requests.Session()
    
    # Retry logic
    retry = Retry(total=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    
    # Mimic a real browser
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    
    return yf.Ticker(symbol, session=session)

def get_history(symbol: str, period: str = "3mo", interval: str = "1d"):
    """Get historical data with fallback periods"""
    ticker = get_ticker(symbol)
    
    # Try requested period first, fall back to shorter periods
    periods_to_try = [period, "1mo", "5d"]
    
    for p in periods_to_try:
        try:
            df = ticker.history(period=p, interval=interval)
            if not df.empty:
                return df
        except Exception:
            continue
    
    return None  # All periods failed