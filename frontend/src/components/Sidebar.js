import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: '🏠', label: 'Dashboard', description: 'Portfolio Overview' },
    { path: '/portfolio', icon: '💼', label: 'Portfolio', description: 'Holdings & Stats' },
    { path: '/transactions', icon: '💸', label: 'Transactions', description: 'Buy/Sell History' },
    { path: '/analytics', icon: '📊', label: 'Analytics', description: 'CAGR, Sharpe, Beta' },
    { path: '/indicators', icon: '📈', label: 'Indicators', description: 'RSI, MACD, SMA' },
    { path: '/predictions', icon: '🤖', label: 'AI Predictions', description: 'LSTM Forecasts' },
    { path: '/alerts', icon: '🔔', label: 'Alerts', description: 'Price Notifications' },
    { path: '/backtesting', icon: '⚡', label: 'Backtesting', description: 'Test Strategies' },
    { path: '/paper-trading', icon: '💰', label: 'Paper Trading', description: 'Virtual Money' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-icon">📊</span>
        <h2>Menu</h2>
      </div>
      
      <nav className="sidebar-menu">
        {menuItems.map((item) => (
          <button
            key={item.path}
            className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="sidebar-item-icon">{item.icon}</span>
            <div className="sidebar-item-content">
              <span className="sidebar-item-label">{item.label}</span>
              <span className="sidebar-item-description">{item.description}</span>
            </div>
          </button>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;