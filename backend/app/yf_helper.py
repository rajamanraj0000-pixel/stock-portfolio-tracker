import yfinance as yf
import pandas as pd

def get_ticker(symbol: str):
    """Get yfinance ticker with curl_cffi session"""
    try:
        from curl_cffi import requests as curl_requests
        session = curl_requests.Session(impersonate="chrome110")
        return yf.Ticker(symbol, session=session)
    except Exception:
        return yf.Ticker(symbol)

def get_history(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """Get historical data - tries multiple methods"""
    
    # Method 1: curl_cffi ticker
    try:
        ticker = get_ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if not df.empty:
            return df
    except Exception:
        pass

    # Method 2: yf.download (different code path, often works when ticker fails)
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         progress=False, auto_adjust=True)
        if not df.empty:
            return df
    except Exception:
        pass

    # Method 3: shorter fallback periods
    for fallback in ["1mo", "5d", "1wk"]:
        if fallback == period:
            continue
        try:
            df = yf.download(symbol, period=fallback, interval=interval,
                             progress=False, auto_adjust=True)
            if not df.empty:
                return df
        except Exception:
            continue

    return pd.DataFrame()  # return empty df, never None

def get_history_range(symbol: str, start_date: str, end_date: str,
                      interval: str = "1d") -> pd.DataFrame:
    """Get historical data for a date range"""
    
    # Method 1: curl_cffi ticker
    try:
        ticker = get_ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        if not df.empty:
            return df
    except Exception:
        pass

    # Method 2: yf.download with date range
    try:
        df = yf.download(symbol, start=start_date, end=end_date,
                         interval=interval, progress=False, auto_adjust=True)
        if not df.empty:
            return df
    except Exception:
        pass

    return pd.DataFrame()