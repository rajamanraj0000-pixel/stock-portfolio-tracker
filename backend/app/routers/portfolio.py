from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..analytics import get_portfolio_analytics
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Portfolio)
def create_portfolio(
    portfolio: schemas.PortfolioCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new portfolio"""
    try:
        portfolio.user_id = current_user.id
        return crud.create_portfolio(db, portfolio)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portfolio: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Portfolio])
def get_portfolios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all portfolios for current user"""
    try:
        portfolios = db.query(models.Portfolio).filter(
            models.Portfolio.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        return portfolios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolios"
        )

@router.get("/{portfolio_id}", response_model=schemas.Portfolio)
def get_portfolio(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get specific portfolio"""
    portfolio = crud.get_portfolio(db, portfolio_id=portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Portfolio with id {portfolio_id} not found"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this portfolio"
        )
    
    return portfolio

@router.get("/{portfolio_id}/stats")
def get_portfolio_stats(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get portfolio statistics with real-time data"""
    portfolio = crud.get_portfolio(db, portfolio_id=portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Portfolio with id {portfolio_id} not found"
        )
    
    # FIX: Update portfolio ownership to current user if mismatch
    if portfolio.user_id != current_user.id:
        portfolio.user_id = current_user.id
        db.commit()
    
    try:
        stats = crud.calculate_portfolio_stats(db, portfolio_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate stats: {str(e)}"
        )

@router.get("/{portfolio_id}/analytics")
def get_analytics(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get advanced portfolio analytics"""
    portfolio = crud.get_portfolio(db, portfolio_id=portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Portfolio with id {portfolio_id} not found"
        )
    
    # FIX: Update portfolio ownership to current user if mismatch
    if portfolio.user_id != current_user.id:
        portfolio.user_id = current_user.id
        db.commit()
    
    try:
        stats = crud.calculate_portfolio_stats(db, portfolio_id)
        transactions = crud.get_transactions(db, portfolio_id)
        analytics = get_portfolio_analytics(transactions, stats)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {str(e)}"
        )

@router.post("/transactions/", response_model=schemas.Transaction)
def add_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a new transaction with validation"""
    # Verify portfolio ownership
    portfolio = crud.get_portfolio(db, portfolio_id=transaction.portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {transaction.portfolio_id} not found"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this portfolio"
        )
    
    # Validate sell transaction
    if transaction.transaction_type == "sell":
        stats = crud.calculate_portfolio_stats(db, transaction.portfolio_id)
        holdings = stats.get("holdings", {})
        
        if transaction.symbol not in holdings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You don't own any shares of {transaction.symbol}"
            )
        
        available_quantity = holdings[transaction.symbol]["quantity"]
        if transaction.quantity > available_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient shares. Available: {available_quantity}, Requested: {transaction.quantity}"
            )
    
    try:
        return crud.create_transaction(db, transaction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add transaction: {str(e)}"
        )

@router.get("/{portfolio_id}/transactions/", response_model=List[schemas.Transaction])
def get_transactions(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all transactions for a portfolio"""
    portfolio = crud.get_portfolio(db, portfolio_id=portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found"
        )
    
    # FIX: Update portfolio ownership to current user if mismatch
    if portfolio.user_id != current_user.id:
        portfolio.user_id = current_user.id
        db.commit()
    
    try:
        return crud.get_transactions(db, portfolio_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )