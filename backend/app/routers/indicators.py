from fastapi import APIRouter, HTTPException, status
from ..indicators import get_all_indicators, calculate_rsi, calculate_macd

router = APIRouter()

@router.get("/{symbol}")
def get_indicators(symbol: str):
    """Get all technical indicators for a stock"""
    try:
        result = get_all_indicators(symbol.upper())
        
        # Check if any indicator has error
        if "error" in result.get("sma_20", {}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to fetch indicators for {symbol}. Invalid symbol or insufficient data."
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate indicators: {str(e)}"
        )

@router.get("/{symbol}/rsi")
def get_rsi(symbol: str, period: int = 14):
    """Get RSI indicator"""
    try:
        result = calculate_rsi(symbol.upper(), period=period)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate RSI: {str(e)}"
        )

@router.get("/{symbol}/macd")
def get_macd(symbol: str):
    """Get MACD indicator"""
    try:
        result = calculate_macd(symbol.upper())
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate MACD: {str(e)}"
        )