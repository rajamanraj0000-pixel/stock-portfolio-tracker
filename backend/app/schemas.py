from pydantic import BaseModel, validator, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class TransactionBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0, description="Quantity must be greater than 0")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    transaction_date: Optional[datetime] = None
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol is required')
        
        v = v.upper().strip()
        
        # Allow: AAPL, TSLA, BTC-USD, ^GSPC, BRK.B
        if not re.match(r'^[A-Z0-9\.\-\^=]{1,10}$', v):
            raise ValueError('Invalid stock symbol format')
        
        return v
    
    @field_validator('quantity', 'price')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Must be greater than 0')
        if v > 1000000000:  # 1 billion max
            raise ValueError('Value too large')
        return round(v, 2)

class TransactionCreate(TransactionBase):
    portfolio_id: int = Field(..., gt=0)

class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    transaction_date: datetime
    
    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Portfolio name is required')
        return v.strip()

class PortfolioCreate(PortfolioBase):
    user_id: int = Field(default=1, gt=0)

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioStats(BaseModel):
    total_investment: float
    current_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    holdings: dict

# Alert schemas with enhanced validation
class AlertCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    alert_type: str = Field(..., pattern="^(price_above|price_below|percent_change)$")
    target_value: float = Field(..., description="Target price or percentage")
    user_id: int = Field(default=1, gt=0)
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol is required')
        
        v = v.upper().strip()
        
        if not re.match(r'^[A-Z0-9\.\-\^=]{1,10}$', v):
            raise ValueError('Invalid stock symbol format')
        
        return v
    
    @field_validator('target_value')
    @classmethod
    def validate_target(cls, v):
        if v <= 0:
            raise ValueError('Target value must be greater than 0')
        if v > 1000000:
            raise ValueError('Target value too large')
        return round(v, 2)

# Paper Trading schemas with validation
class PaperTradeCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    trade_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    user_id: int = Field(default=1, gt=0)
    notes: Optional[str] = Field(None, max_length=200)
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol is required')
        
        v = v.upper().strip()
        
        if not re.match(r'^[A-Z0-9\.\-\^=]{1,10}$', v):
            raise ValueError('Invalid stock symbol format')
        
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 1000000:
            raise ValueError('Quantity too large')
        return round(v, 2)
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v:
            return v.strip()[:200]
        return v

# Backtesting schemas
class BacktestRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    strategy: str = Field(..., pattern="^(sma_crossover|rsi_strategy|buy_and_hold)$")
    start_date: str
    end_date: str
    initial_capital: float = Field(default=10000, gt=0)
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol is required')
        
        v = v.upper().strip()
        
        if not re.match(r'^[A-Z0-9\.\-\^=]{1,10}$', v):
            raise ValueError('Invalid stock symbol format')
        
        return v
    
    @field_validator('initial_capital')
    @classmethod
    def validate_capital(cls, v):
        if v < 100:
            raise ValueError('Initial capital must be at least $100')
        if v > 10000000:
            raise ValueError('Initial capital too large')
        return round(v, 2)
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        start = info.data.get('start_date')
        if start and v <= start:
            raise ValueError('End date must be after start date')
        return v