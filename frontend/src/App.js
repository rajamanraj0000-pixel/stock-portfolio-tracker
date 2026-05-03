import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './components/Login';
import Signup from './components/Signup';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import TransactionsPage from './pages/TransactionsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import IndicatorsPage from './pages/IndicatorsPage';
import PredictionsPage from './pages/PredictionsPage';
import AlertsPage from './pages/AlertsPage';
import BacktestingPage from './pages/BacktestingPage';
import PaperTradingPage from './pages/PaperTradingPage';

import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            
            {/* Protected Routes with Layout */}
            <Route path="/dashboard" element={
              <ProtectedRoute><Layout><DashboardPage /></Layout></ProtectedRoute>
            } />
            <Route path="/portfolio" element={
              <ProtectedRoute><Layout><PortfolioPage /></Layout></ProtectedRoute>
            } />
            <Route path="/transactions" element={
              <ProtectedRoute><Layout><TransactionsPage /></Layout></ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute><Layout><AnalyticsPage /></Layout></ProtectedRoute>
            } />
            <Route path="/indicators" element={
              <ProtectedRoute><Layout><IndicatorsPage /></Layout></ProtectedRoute>
            } />
            <Route path="/predictions" element={
              <ProtectedRoute><Layout><PredictionsPage /></Layout></ProtectedRoute>
            } />
            <Route path="/alerts" element={
              <ProtectedRoute><Layout><AlertsPage /></Layout></ProtectedRoute>
            } />
            <Route path="/backtesting" element={
              <ProtectedRoute><Layout><BacktestingPage /></Layout></ProtectedRoute>
            } />
            <Route path="/paper-trading" element={
              <ProtectedRoute><Layout><PaperTradingPage /></Layout></ProtectedRoute>
            } />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 Not Found */}
            <Route path="*" element={
              <div className="error-state" style={{minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <div>
                  <h1>404 - Page Not Found</h1>
                  <p>The page you're looking for doesn't exist.</p>
                  <button onClick={() => window.location.href = '/dashboard'} className="retry-button">
                    Go to Dashboard
                  </button>
                </div>
              </div>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;