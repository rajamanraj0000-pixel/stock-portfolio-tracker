from fastapi import APIRouter ,  HTTPException, status
from pydantic import BaseModel , Field, field_validator
from ..backtesting import backtest_strategy
from ..schemas import BacktestRequest

router = APIRouter()

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str  # 'sma_crossover', 'rsi_strategy', 'buy_and_hold'
    start_date: str
    end_date: str
    initial_capital: float = 10000
    short_window: int = 20
    long_window: int = 50
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70

@router.post("/")
def run_backtest(request: BacktestRequest):
    """Run strategy backtest with validation"""
    try:
        result = backtest_strategy(
            symbol=request.symbol,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
        
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
            detail=f"Backtest failed: {str(e)}"
        )

@router.get("/{symbol}/quick")
def quick_backtest(symbol: str, strategy: str = "sma_crossover", months: int = 6):
    """Run a quick backtest for the last N months"""
    from datetime import datetime, timedelta
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30*months)).strftime('%Y-%m-%d')
    
    return backtest_strategy(
        symbol=symbol,
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=10000
    )