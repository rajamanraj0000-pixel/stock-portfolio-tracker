from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolios = relationship("Portfolio", back_populates="owner")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="portfolios")
    transactions = relationship("Transaction", back_populates="portfolio")
    
    __table_args__ = (
        Index('idx_portfolio_user', 'user_id'),
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    transaction_type = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_txn_portfolio', 'portfolio_id'),
        Index('idx_txn_symbol', 'symbol'),
        Index('idx_txn_date', 'transaction_date'),
        Index('idx_txn_portfolio_symbol', 'portfolio_id', 'symbol'),
    )

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    alert_type = Column(String)
    target_value = Column(Float)
    current_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_alert_user', 'user_id'),
        Index('idx_alert_active', 'is_active', 'is_triggered'),
        Index('idx_alert_user_active', 'user_id', 'is_active'),
    )

class PaperTrade(Base):
    __tablename__ = "paper_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    trade_type = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    virtual_cash = Column(Float)
    trade_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_paper_user', 'user_id'),
        Index('idx_paper_date', 'trade_date'),
        Index('idx_paper_user_symbol', 'user_id', 'symbol'),
    )

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_watchlist_user', 'user_id'),
        Index('idx_watchlist_user_symbol', 'user_id', 'symbol'),
    )