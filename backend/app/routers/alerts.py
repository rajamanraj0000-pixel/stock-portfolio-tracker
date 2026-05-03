from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models import Alert
from ..alerts import check_all_alerts
from ..schemas import AlertCreate

router = APIRouter()

class AlertResponse(BaseModel):
    id: int
    symbol: str
    alert_type: str
    target_value: float
    current_value: float | None
    is_active: bool
    is_triggered: bool
    created_at: datetime
    triggered_at: datetime | None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=AlertResponse)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create alert with validation"""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[AlertResponse])
def get_alerts(user_id: int = 1, active_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Alert).filter(Alert.user_id == user_id)
    if active_only:
        query = query.filter(Alert.is_active == True, Alert.is_triggered == False)
    return query.all()

@router.get("/check")
def check_alerts(user_id: int = 1, db: Session = Depends(get_db)):
    triggered = check_all_alerts(db, user_id)
    return {"triggered_count": len(triggered), "triggered_alerts": triggered}

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}

@router.put("/{alert_id}/deactivate")
def deactivate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = False
    db.commit()
    return {"message": "Alert deactivated successfully"}