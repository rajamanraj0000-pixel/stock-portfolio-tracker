from fastapi import APIRouter, HTTPException, status
import yfinance as yf
from typing import Dict
from ..stock_cache import get_stock_info_cached, get_current_price_cached

router = APIRouter()

@router.get("/{symbol}")
def get_stock_data(symbol: str) -> Dict:
    """Get current stock data"""
    result = get_stock_info_cached(symbol)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )

    if result.get("current_price", 0) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock symbol '{symbol}' not found or invalid"
        )

    return result


@router.get("/{symbol}/history")
def get_stock_history(symbol: str, period: str = "1mo"):
    """Get historical stock data"""
    try:
        stock = yf.Ticker(symbol.upper())
        hist = stock.history(period=period)
        
        if hist.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for {symbol}"
            )
        
        data = []

        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "price": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/{symbol}/price")
def get_stock_price(symbol: str):
    """Get cached stock price only"""
    price = get_current_price_cached(symbol)

    if price == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to fetch price for {symbol}"
        )

    return {
        "symbol": symbol.upper(),
        "price": round(price, 2)
    }