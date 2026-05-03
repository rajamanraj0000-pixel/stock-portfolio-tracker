from sqlalchemy.orm import Session
from typing import Dict, List
from .models import PaperTrade
from datetime import datetime
from .yf_helper import get_ticker

def get_current_price(symbol: str) -> float:
    """Get current stock price directly via yfinance with headers"""
    try:
        ticker = get_ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        return 0
    except Exception:
        return 0

def get_paper_portfolio_stats(db: Session, user_id: int) -> Dict:
    """Calculate paper trading portfolio statistics"""
    
    trades = db.query(PaperTrade).filter(PaperTrade.user_id == user_id).order_by(PaperTrade.trade_date).all()
    
    if not trades:
        return {
            "total_cash": 100000,  # Starting cash
            "holdings": {},
            "portfolio_value": 100000,
            "total_profit_loss": 0,
            "total_profit_loss_percentage": 0,
            "num_trades": 0
        }
    
    # Calculate holdings
    holdings = {}
    total_cash = trades[-1].virtual_cash  # Latest cash balance
    
    for trade in trades:
        symbol = trade.symbol
        
        if symbol not in holdings:
            holdings[symbol] = {
                "quantity": 0,
                "total_invested": 0,
                "avg_price": 0
            }
        
        if trade.trade_type == "buy":
            old_quantity = holdings[symbol]["quantity"]
            old_invested = holdings[symbol]["total_invested"]
            
            new_quantity = old_quantity + trade.quantity
            new_invested = old_invested + (trade.quantity * trade.price)
            
            holdings[symbol]["quantity"] = new_quantity
            holdings[symbol]["total_invested"] = new_invested
            holdings[symbol]["avg_price"] = new_invested / new_quantity if new_quantity > 0 else 0
            
        elif trade.trade_type == "sell":
            holdings[symbol]["quantity"] -= trade.quantity
            if holdings[symbol]["quantity"] > 0:
                holdings[symbol]["total_invested"] = holdings[symbol]["quantity"] * holdings[symbol]["avg_price"]
            else:
                holdings[symbol]["total_invested"] = 0
    
    # Remove zero holdings
    holdings = {k: v for k, v in holdings.items() if v["quantity"] > 0}
    
    # Calculate current values
    holdings_value = 0
    holdings_detail = {}
    
    for symbol, data in holdings.items():
        current_price = get_current_price(symbol)
        current_value = data["quantity"] * current_price
        invested = data["total_invested"]
        profit_loss = current_value - invested
        profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
        
        holdings_value += current_value
        
        holdings_detail[symbol] = {
            "quantity": data["quantity"],
            "avg_price": round(data["avg_price"], 2),
            "current_price": round(current_price, 2),
            "invested": round(invested, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percentage": round(profit_loss_pct, 2)
        }
    
    portfolio_value = total_cash + holdings_value
    initial_capital = 100000
    total_profit_loss = portfolio_value - initial_capital
    total_profit_loss_pct = (total_profit_loss / initial_capital) * 100
    
    return {
        "total_cash": round(total_cash, 2),
        "holdings": holdings_detail,
        "holdings_value": round(holdings_value, 2),
        "portfolio_value": round(portfolio_value, 2),
        "initial_capital": initial_capital,
        "total_profit_loss": round(total_profit_loss, 2),
        "total_profit_loss_percentage": round(total_profit_loss_pct, 2),
        "num_trades": len(trades)
    }

def execute_paper_trade(db: Session, user_id: int, symbol: str, trade_type: str, quantity: float, notes: str = None) -> Dict:
    """Execute a paper trade"""
    
    # Get current portfolio stats
    stats = get_paper_portfolio_stats(db, user_id)
    current_cash = stats["total_cash"]
    
    # Get current price
    current_price = get_current_price(symbol)
    
    if current_price == 0:
        return {"error": "Unable to fetch current price"}
    
    # Calculate trade value
    trade_value = quantity * current_price
    
    if trade_type == "buy":
        # Check if enough cash
        if trade_value > current_cash:
            return {"error": f"Insufficient cash. Need ${trade_value:.2f}, have ${current_cash:.2f}"}
        
        new_cash = current_cash - trade_value
        
    elif trade_type == "sell":
        # Check if user has enough shares
        holdings = stats.get("holdings", {})
        
        if symbol not in holdings:
            return {"error": f"You don't own any {symbol} shares"}
        
        if holdings[symbol]["quantity"] < quantity:
            return {"error": f"Insufficient shares. You have {holdings[symbol]['quantity']}, trying to sell {quantity}"}
        
        new_cash = current_cash + trade_value
    else:
        return {"error": "Invalid trade type"}
    
    # Create trade record
    trade = PaperTrade(
        user_id=user_id,
        symbol=symbol,
        trade_type=trade_type,
        quantity=quantity,
        price=current_price,
        virtual_cash=new_cash,
        notes=notes
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return {
        "success": True,
        "trade": {
            "id": trade.id,
            "symbol": trade.symbol,
            "trade_type": trade.trade_type,
            "quantity": trade.quantity,
            "price": round(trade.price, 2),
            "total_value": round(trade_value, 2),
            "virtual_cash": round(trade.virtual_cash, 2),
            "trade_date": trade.trade_date.isoformat()
        }
    }