from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
import yfinance as yf
from collections import defaultdict
from .stock_cache import get_current_price_cached

def create_portfolio(db: Session, portfolio: schemas.PortfolioCreate):
    db_portfolio = models.Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Portfolio).offset(skip).limit(limit).all()

def get_portfolio(db: Session, portfolio_id: int):
    return db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, portfolio_id: int):
    return db.query(models.Transaction).filter(
        models.Transaction.portfolio_id == portfolio_id
    ).order_by(models.Transaction.transaction_date.desc()).all()

def calculate_portfolio_stats(db: Session, portfolio_id: int):
    """Calculate portfolio statistics including P&L"""
    transactions = get_transactions(db, portfolio_id)
    
    if not transactions:
        return {
            "total_investment": 0,
            "current_value": 0,
            "total_profit_loss": 0,
            "total_profit_loss_percentage": 0,
            "holdings": {}
        }
    
    # Calculate holdings using FIFO
    holdings = defaultdict(lambda: {"quantity": 0, "avg_price": 0, "total_invested": 0})
    
    for txn in reversed(transactions):  # Process oldest first for FIFO
        symbol = txn.symbol
        
        if txn.transaction_type == "buy":
            old_quantity = holdings[symbol]["quantity"]
            old_invested = holdings[symbol]["total_invested"]
            
            new_quantity = old_quantity + txn.quantity
            new_invested = old_invested + (txn.quantity * txn.price)
            
            holdings[symbol]["quantity"] = new_quantity
            holdings[symbol]["total_invested"] = new_invested
            holdings[symbol]["avg_price"] = new_invested / new_quantity if new_quantity > 0 else 0
            
        elif txn.transaction_type == "sell":
            holdings[symbol]["quantity"] -= txn.quantity
            # Reduce invested amount proportionally
            if holdings[symbol]["quantity"] > 0:
                holdings[symbol]["total_invested"] = holdings[symbol]["quantity"] * holdings[symbol]["avg_price"]
            else:
                holdings[symbol]["total_invested"] = 0
    
    # Remove zero holdings
    holdings = {k: v for k, v in holdings.items() if v["quantity"] > 0}
    
    # Calculate current values
    total_investment = 0
    current_value = 0
    holdings_detail = {}
    
    for symbol, data in holdings.items():
        try:
            stock = yf.Ticker(symbol)
            current_price = get_current_price_cached(symbol)
            
            if current_price == 0:
                current_price = data["avg_price"]
        except:
            current_price = data["avg_price"]
        
        invested = data["total_invested"]
        value = data["quantity"] * current_price
        profit_loss = value - invested
        profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
        
        total_investment += invested
        current_value += value
        
        holdings_detail[symbol] = {
            "quantity": data["quantity"],
            "avg_price": round(data["avg_price"], 2),
            "current_price": round(current_price, 2),
            "invested": round(invested, 2),
            "current_value": round(value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percentage": round(profit_loss_pct, 2)
        }
    
    total_profit_loss = current_value - total_investment
    total_profit_loss_pct = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "total_investment": round(total_investment, 2),
        "current_value": round(current_value, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "total_profit_loss_percentage": round(total_profit_loss_pct, 2),
        "holdings": holdings_detail
    }