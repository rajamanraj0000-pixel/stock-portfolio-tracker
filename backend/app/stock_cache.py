import time
import re
import threading
from .yf_helper import get_ticker
from typing import Dict, Any

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()

DEFAULT_TTL = 60  # seconds


def normalize_symbol(symbol: str) -> str:
    """Normalize and validate stock symbol"""
    if not symbol:
        raise ValueError("Stock symbol is required")

    symbol = symbol.upper().strip()

    # Allows AAPL, TSLA, BTC-USD, ^GSPC, BRK.B
    if not re.match(r"^[A-Z0-9\.\-\^=]{1,20}$", symbol):
        raise ValueError("Invalid stock symbol format")

    return symbol


def _get_cache_key(prefix: str, symbol: str) -> str:
    return f"{prefix}:{symbol}"


def _get_cached(key: str, ttl: int = DEFAULT_TTL):
    """Get cached value if not expired"""
    with _cache_lock:
        item = _cache.get(key)

        if not item:
            return None

        if time.time() - item["timestamp"] > ttl:
            del _cache[key]
            return None

        return item["value"]


def _set_cached(key: str, value):
    """Set cache value"""
    with _cache_lock:
        _cache[key] = {
            "value": value,
            "timestamp": time.time()
        }


def get_current_price_cached(symbol: str, ttl: int = DEFAULT_TTL) -> float:
    """Get current stock price with cache"""
    try:
        symbol = normalize_symbol(symbol)
    except ValueError:
        return 0.0

    key = _get_cache_key("price", symbol)

    cached_price = _get_cached(key, ttl)
    if cached_price is not None:
        return cached_price

    price = 0.0

    try:
        stock = get_ticker(symbol)

        # Fast method first
        try:
            fast_info = stock.fast_info
            price = fast_info.get("lastPrice", 0) or fast_info.get("last_price", 0)
        except:
            price = 0.0

        # Fallback to info
        if not price:
            try:
                info = stock.info
                price = (
                    info.get("currentPrice", 0)
                    or info.get("regularMarketPrice", 0)
                    or info.get("previousClose", 0)
                )
            except:
                price = 0.0

        price = float(price) if price else 0.0

        if price > 0:
            _set_cached(key, price)

        return price

    except:
        return 0.0


def get_stock_info_cached(symbol: str, ttl: int = DEFAULT_TTL) -> Dict:
    """Get stock info with cache"""
    try:
        symbol = normalize_symbol(symbol)
    except ValueError as e:
        return {"error": str(e)}

    key = _get_cache_key("info", symbol)

    cached_info = _get_cached(key, ttl)
    if cached_info is not None:
        return cached_info

    try:
        stock = get_ticker(symbol)
        info = stock.info or {}

        current_price = get_current_price_cached(symbol, ttl)

        result = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "company_name": info.get("longName", symbol),
            "currency": info.get("currency", "USD"),
            "market_cap": info.get("marketCap", 0),
            "volume": info.get("volume", 0),
            "previous_close": info.get("previousClose", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0)
        }

        _set_cached(key, result)
        return result

    except Exception as e:
        return {
            "error": f"Unable to fetch stock info: {str(e)}"
        }


def clear_stock_cache():
    """Clear all cache"""
    with _cache_lock:
        _cache.clear()


def get_cache_stats():
    """Return cache stats"""
    with _cache_lock:
        return {
            "cached_items": len(_cache),
            "keys": list(_cache.keys())
        }