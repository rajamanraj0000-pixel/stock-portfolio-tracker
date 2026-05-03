import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import Toast from './Toast';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [triggeredAlerts, setTriggeredAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [formData, setFormData] = useState({ 
    symbol: '', 
    alert_type: 'price_above', 
    target_value: '', 
    user_id: 1 
  });

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(checkAlerts, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try { 
      const response = await api.getAlerts(1, false); 
      setAlerts(response.data); 
    } catch (e) { 
      setToast({ message: 'Failed to load alerts', type: 'error' });
    }
  };

  const checkAlerts = async () => {
    try { 
      const response = await api.checkAlerts(1); 
      if (response.data.triggered_alerts?.length > 0) {
        setTriggeredAlerts(response.data.triggered_alerts);
        setToast({ 
          message: `${response.data.triggered_alerts.length} alert(s) triggered!`, 
          type: 'warning' 
        });
      }
    } catch (e) { 
      console.error('Error checking alerts:', e); 
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.symbol.trim()) {
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return;
    }
    
    if (!formData.target_value || parseFloat(formData.target_value) <= 0) {
      setToast({ message: 'Target value must be greater than 0', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      await api.createAlert({ 
        ...formData, 
        target_value: parseFloat(formData.target_value) 
      });
      setToast({ message: '🔔 Alert created successfully!', type: 'success' });
      setFormData({ symbol: '', alert_type: 'price_above', target_value: '', user_id: 1 });
      fetchAlerts();
    } catch (e) { 
      setToast({ 
        message: e.response?.data?.detail || 'Failed to create alert', 
        type: 'error' 
      });
    }
    setLoading(false);
  };

  const handleDelete = async (alertId) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;
    
    try {
      await api.deleteAlert(alertId);
      setToast({ message: 'Alert deleted', type: 'success' });
      fetchAlerts();
    } catch (e) {
      setToast({ message: 'Failed to delete alert', type: 'error' });
    }
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="alerts-section">
        <h2>🔔 Price Alerts</h2>
        
        {triggeredAlerts.length > 0 && (
          <div className="triggered-alerts">
            <h3>⚠️ Triggered Alerts</h3>
            {triggeredAlerts.map((a, i) => (
              <div key={i} className="triggered-alert">
                <span className="alert-icon">🔔</span>
                <span className="alert-message">{a.message}</span>
              </div>
            ))}
          </div>
        )}
        
        <div className="create-alert">
          <h3>Create New Alert</h3>
          <form onSubmit={handleSubmit} className="alert-form">
            <input 
              type="text" 
              placeholder="Symbol (e.g., AAPL)" 
              value={formData.symbol} 
              onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})} 
              required 
              disabled={loading}
            />
            <select 
              value={formData.alert_type} 
              onChange={(e) => setFormData({...formData, alert_type: e.target.value})}
              disabled={loading}
            >
              <option value="price_above">Price Above</option>
              <option value="price_below">Price Below</option>
              <option value="percent_change">Percent Change</option>
            </select>
            <input 
              type="number" 
              step="0.01" 
              placeholder="Target Value"
              value={formData.target_value} 
              onChange={(e) => setFormData({...formData, target_value: e.target.value})} 
              required 
              disabled={loading}
              min="0.01"
            />
            <button type="submit" disabled={loading}>
              {loading ? '⏳ Creating...' : '🔔 Create Alert'}
            </button>
          </form>
        </div>

        <div className="alerts-list">
          <h3>Active Alerts ({alerts.filter(a => a.is_active && !a.is_triggered).length})</h3>
          
          {alerts.filter(a => a.is_active && !a.is_triggered).length === 0 ? (
            <div className="no-alerts">
              <p>📭 No active alerts</p>
              <p>Create an alert to get notified when price targets are hit</p>
            </div>
          ) : (
            <div className="alerts-grid">
              {alerts.filter(a => a.is_active && !a.is_triggered).map((alert) => (
                <div key={alert.id} className="alert-card">
                  <div className="alert-header">
                    <span className="alert-symbol">{alert.symbol}</span>
                    <button 
                      className="delete-btn" 
                      onClick={() => handleDelete(alert.id)}
                      title="Delete alert"
                    >
                      ×
                    </button>
                  </div>
                  <div className="alert-details">
                    <p className="alert-type">
                      {alert.alert_type.replace('_', ' ').toUpperCase()}
                    </p>
                    <p className="alert-target">${alert.target_value}</p>
                    <p className="alert-date">
                      Created: {new Date(alert.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default Alerts;