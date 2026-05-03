from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Watchlist, User
from ..auth import get_current_user
import yfinance as yf
from ..stock_cache import get_current_price_cached

router = APIRouter()

class WatchlistCreate(BaseModel):
    symbol: str
    notes: str | None = None

@router.post("/")
def add_to_watchlist(
    item: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    symbol = item.symbol.upper().strip()

    if not symbol:
        raise HTTPException(status_code=400, detail="Stock symbol is required")

    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol == symbol
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already in watchlist")
    
    watchlist_item = Watchlist(
        user_id=current_user.id,
        symbol=symbol,
        notes=item.notes
    )

    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)

    return {
        "id": watchlist_item.id,
        "symbol": watchlist_item.symbol,
        "notes": watchlist_item.notes,
        "added_at": watchlist_item.added_at,
        "message": "Added to watchlist"
    }

@router.get("/")
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id
    ).order_by(Watchlist.added_at.desc()).all()
    
    result = []

    for item in items:
        current_price = 0

        try:
            stock = yf.Ticker(item.symbol)
            current_price = get_current_price_cached(item.symbol)
            if current_price == 0:
                current_price = get_current_price_cached(item.symbol)
        except:
            current_price = 0

        result.append({
            "id": item.id,
            "symbol": item.symbol,
            "current_price": round(float(current_price), 2) if current_price else 0,
            "notes": item.notes,
            "added_at": item.added_at
        })
    
    return result

@router.delete("/{item_id}")
def remove_from_watchlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Watchlist).filter(
        Watchlist.id == item_id,
        Watchlist.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    db.delete(item)
    db.commit()

    return {"message": "Removed from watchlist"}