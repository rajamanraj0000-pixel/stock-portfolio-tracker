import yfinance as yf
from sqlalchemy.orm import Session
from typing import List, Dict
from .models import Alert
from datetime import datetime
from .database import get_db
from .models import Alert
from .stock_cache import get_current_price_cached

def check_price_alert(alert: Alert) -> bool:
    """Check if price alert should be triggered"""
    try:
        stock = yf.Ticker(alert.symbol)
        current_price = get_current_price_cached(alert.symbol)

        if current_price == 0:
            return False
        
        alert.current_value = current_price
        
        if alert.alert_type == 'price_above':
            return current_price >= alert.target_value
        elif alert.alert_type == 'price_below':
            return current_price <= alert.target_value
        
        return False
    except:
        return False

def check_percent_change_alert(alert: Alert) -> bool:
    """Check if percentage change alert should be triggered"""
    try:
        stock = yf.Ticker(alert.symbol)
        hist = stock.history(period='1d')
        
        if hist.empty:
            return False
        
        current_price = hist['Close'].iloc[-1]
        previous_close = stock.info.get('previousClose', current_price)
        
        if previous_close == 0:
            return False
        
        percent_change = ((current_price - previous_close) / previous_close) * 100
        alert.current_value = percent_change
        
        # For positive change
        if alert.target_value > 0:
            return percent_change >= alert.target_value
        # For negative change
        else:
            return percent_change <= alert.target_value
            
    except:
        return False

def check_all_alerts(db: Session, user_id: int = None) -> List[Dict]:
    """Check all active alerts and trigger if conditions met"""
    query = db.query(Alert).filter(Alert.is_active == True, Alert.is_triggered == False)
    
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    
    alerts = query.all()
    triggered_alerts = []
    
    for alert in alerts:
        should_trigger = False
        
        if alert.alert_type in ['price_above', 'price_below']:
            should_trigger = check_price_alert(alert)
        elif alert.alert_type == 'percent_change':
            should_trigger = check_percent_change_alert(alert)
        
        if should_trigger:
            alert.is_triggered = True
            alert.triggered_at = datetime.utcnow()
            db.commit()
            
            triggered_alerts.append({
                'id': alert.id,
                'symbol': alert.symbol,
                'alert_type': alert.alert_type,
                'target_value': alert.target_value,
                'current_value': alert.current_value,
                'message': generate_alert_message(alert)
            })
    
    return triggered_alerts

def generate_alert_message(alert: Alert) -> str:
    """Generate human-readable alert message"""
    if alert.alert_type == 'price_above':
        return f"{alert.symbol} has reached ${alert.current_value:.2f} (target: ${alert.target_value:.2f})"
    elif alert.alert_type == 'price_below':
        return f"{alert.symbol} has dropped to ${alert.current_value:.2f} (target: ${alert.target_value:.2f})"
    elif alert.alert_type == 'percent_change':
        return f"{alert.symbol} changed by {alert.current_value:.2f}% (target: {alert.target_value:.2f}%)"
    return "Alert triggered"