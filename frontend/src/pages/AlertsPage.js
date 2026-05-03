import React from 'react';
import Alerts from '../components/Alerts';

function AlertsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🔔 Price Alerts</h1>
        <p>Get notified when stocks hit your target prices</p>
      </div>
      <Alerts />
    </div>
  );
}

export default AlertsPage;