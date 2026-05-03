import yfinance as yf

def get_ticker(symbol: str):
    """Get yfinance ticker - let yfinance handle session internally"""
    try:
        # Try with curl_cffi (required by new yfinance versions)
        from curl_cffi import requests as curl_requests
        session = curl_requests.Session(impersonate="chrome")
        return yf.Ticker(symbol, session=session)
    except Exception:
        # Fallback - no session, let yfinance handle it
        return yf.Ticker(symbol)

def get_history(symbol: str, period: str = "3mo", interval: str = "1d"):
    """Get historical data with fallback periods"""
    ticker = get_ticker(symbol)
    periods_to_try = [period, "1mo", "5d"]
    for p in periods_to_try:
        try:
            df = ticker.history(period=p, interval=interval)
            if not df.empty:
                return df
        except Exception:
            continue
    return None