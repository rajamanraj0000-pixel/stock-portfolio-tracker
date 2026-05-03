import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
// Get token from localStorage
const getToken = () => localStorage.getItem('access_token');

// Create axios instance with auth header
const apiClient = axios.create({
  baseURL: API_BASE_URL
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;

      // 🔐 Unauthorized → logout
      if (status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }

      // 🚫 Forbidden
      if (status === 403) {
        return Promise.reject({
          message: "Access denied. You don't have permission.",
          response: error.response
        });
      }

      // ❌ Not Found
      if (status === 404) {
        return Promise.reject({
          message: error.response.data?.detail || "Resource not found",
          response: error.response
        });
      }

      // ⚠️ Server Error
      if (status >= 500) {
        return Promise.reject({
          message: "Server error. Please try again later.",
          response: error.response
        });
      }

      return Promise.reject({
        message: error.response.data?.detail || "Something went wrong",
        response: error.response
      });
    }

    // 🌐 Network error (no response from server)
    if (error.request) {
      return Promise.reject({
        message: "Network error. Please check your internet connection.",
        isNetworkError: true
      });
    }

    return Promise.reject({
      message: error.message || "An unexpected error occurred"
    });
  }
);

export const api = {
  // Auth endpoints - NEW
  signup: (data) => axios.post(`${API_BASE_URL}/auth/signup`, data),
  
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return axios.post(`${API_BASE_URL}/auth/login`, formData);
  },
  
  getCurrentUser: () => apiClient.get('/auth/me'),
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  
  // All other endpoints - use apiClient for authenticated requests
  getPortfolios: () => apiClient.get('/portfolio/'),
  
  getPortfolio: (id) => apiClient.get(`/portfolio/${id}`),
  
  createPortfolio: (data) => apiClient.post('/portfolio/', data),
  
  getPortfolioStats: (id) => apiClient.get(`/portfolio/${id}/stats`),
  
  getAnalytics: (id) => apiClient.get(`/portfolio/${id}/analytics`),
  
  addTransaction: (data) => apiClient.post('/portfolio/transactions/', data),
  
  getTransactions: (portfolioId) => 
    apiClient.get(`/portfolio/${portfolioId}/transactions/`),
  
  getStockData: (symbol) => apiClient.get(`/stocks/${symbol}`),
  
  getIndicators: (symbol) => apiClient.get(`/indicators/${symbol}`),
  
  getRSI: (symbol) => apiClient.get(`/indicators/${symbol}/rsi`),
  
  getMACD: (symbol) => apiClient.get(`/indicators/${symbol}/macd`),
  
  getLSTMPrediction: (symbol, days = 30) => 
    apiClient.get(`/predictions/${symbol}?days=${days}&use_lstm=true`),
  
  getQuickPrediction: (symbol) => 
    apiClient.get(`/predictions/${symbol}/quick`),
  
  createAlert: (data) => apiClient.post('/alerts/', data),
  
  getAlerts: (userId = 1, activeOnly = false) => 
    apiClient.get(`/alerts/?user_id=${userId}&active_only=${activeOnly}`),
  
  checkAlerts: (userId = 1) => 
    apiClient.get(`/alerts/check?user_id=${userId}`),
  
  deleteAlert: (alertId) => apiClient.delete(`/alerts/${alertId}`),
  
  deactivateAlert: (alertId) => 
    apiClient.put(`/alerts/${alertId}/deactivate`),
  
  runBacktest: (data) => apiClient.post('/backtest/', data),
  
  quickBacktest: (symbol, strategy = 'sma_crossover', months = 6) => 
    apiClient.get(`/backtest/${symbol}/quick?strategy=${strategy}&months=${months}`),
  
  executePaperTrade: (data) => apiClient.post('/paper/trade', data),
  
  getPaperPortfolio: (userId = 1) => 
    apiClient.get(`/paper/portfolio?user_id=${userId}`),
  
  getPaperTrades: (userId = 1, limit = 50) => 
    apiClient.get(`/paper/trades?user_id=${userId}&limit=${limit}`),
  
  resetPaperPortfolio: (userId = 1) => 
    apiClient.post(`/paper/reset?user_id=${userId}`),

  // Watchlist endpoints (✅ FIXED POSITION + removed extra ')')
  addToWatchlist: (data) => apiClient.post('/watchlist/', data),
  getWatchlist: () => apiClient.get('/watchlist/'),
  removeFromWatchlist: (id) => apiClient.delete(`/watchlist/${id}`),
};