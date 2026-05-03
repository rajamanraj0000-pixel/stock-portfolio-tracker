import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(email, password);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error || "Invalid credentials");
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <h1>📊 Stock Portfolio Tracker</h1>
                <h2>Login to Your Account</h2>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            placeholder="your@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="auth-button" disabled={loading}>
                        {loading ? (
                            <span className="spinner-container">
                                <span className="spinner"></span> Logging in...
                            </span>
                        ) : (
                            "Login"
                        )}
                    </button>
                </form>

                <p className="auth-link">
                    Don't have an account? <Link to="/signup">Sign up here</Link>
                </p>
            </div>
        </div>
    );
}

export default Login;