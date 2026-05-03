from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import PaperTrade, User
from ..paper_trading import execute_paper_trade, get_paper_portfolio_stats
from ..auth import get_current_user
from ..schemas import PaperTradeCreate

router = APIRouter()

@router.post("/trade")
def create_paper_trade(
    trade: PaperTradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a paper trade with validation"""
    try:
        result = execute_paper_trade(
            db=db,
            user_id=current_user.id,
            symbol=trade.symbol,
            trade_type=trade.trade_type,
            quantity=trade.quantity,
            notes=trade.notes
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
            detail=f"Trade execution failed: {str(e)}"
        )

@router.get("/portfolio")
def get_paper_portfolio(
    user_id: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paper trading portfolio stats"""
    try:
        stats = get_paper_portfolio_stats(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio: {str(e)}"
        )

@router.get("/trades")
def get_paper_trades(
    user_id: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paper trading history"""
    try:
        trades = db.query(PaperTrade).filter(
            PaperTrade.user_id == current_user.id
        ).order_by(PaperTrade.trade_date.desc()).limit(limit).all()
        
        return trades
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trades"
        )

@router.post("/reset")
def reset_paper_portfolio(
    user_id: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset paper trading portfolio"""
    try:
        db.query(PaperTrade).filter(
            PaperTrade.user_id == current_user.id
        ).delete()
        db.commit()
        
        return {
            "success": True,
            "message": "Paper trading portfolio reset successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset portfolio: {str(e)}"
        )