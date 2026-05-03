import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_ticker(symbol: str):
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
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
    ticker = get_ticker(symbol)
    for p in [period, "1mo", "5d"]:
        try:
            df = ticker.history(period=p, interval=interval)
            if not df.empty:
                return df
        except Exception:
            continue
    return None