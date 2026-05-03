from fastapi import APIRouter, HTTPException, status, Query
from ..ml_predictions import predict_stock

router = APIRouter()

@router.get("/{symbol}")
def get_prediction(
    symbol: str, 
    days: int = Query(default=30, ge=1, le=90),
    use_lstm: bool = Query(default=True)
):
    """Get AI price prediction for a stock"""
    try:
        result = predict_stock(
            symbol=symbol.upper(), 
            days_ahead=days, 
            use_lstm=use_lstm
        )
        
        if not result.get("prediction_available", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Prediction not available")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@router.get("/{symbol}/quick")
def get_quick_prediction(symbol: str):
    """Get quick trend-based prediction"""
    try:
        result = predict_stock(
            symbol=symbol.upper(), 
            days_ahead=7, 
            use_lstm=False
        )
        
        if not result.get("prediction_available", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Prediction not available")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )