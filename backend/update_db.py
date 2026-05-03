from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
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

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="portfolios")
    transactions = relationship("Transaction", back_populates="portfolio")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    transaction_type = Column(String)  # 'buy' or 'sell'
    quantity = Column(Float)
    price = Column(Float)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="transactions")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    alert_type = Column(String)  # 'price_above', 'price_below', 'percent_change'
    target_value = Column(Float)
    current_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    user = relationship("User")