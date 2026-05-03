import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    
    const getInitialTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme === 'dark';
        }
        return false;
    };

    const [darkMode, setDarkMode] = useState(getInitialTheme);

    useEffect(() => {
        const root = document.documentElement;
        if (darkMode) {
            root.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            root.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }, [darkMode]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const toggleTheme = () => {
        setDarkMode(!darkMode);
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand">
                    <button 
                        onClick={toggleTheme} 
                        className="theme-toggle-left"
                        title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                    >
                        {darkMode ? '☀️' : '🌙'}
                    </button>
                    <div className="brand-text">
                        <span className="brand-sub">AMAN STOCK PORTFOLIO TRACKER</span>
                    </div>
                </div>

                <div className="navbar-right">
                    <div className="user-info">
                        <span className="user-icon">👤</span>
                        <span className="user-email">{user?.email}</span>
                    </div>
                    <button onClick={handleLogout} className="logout-button">
                        🚪 Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;