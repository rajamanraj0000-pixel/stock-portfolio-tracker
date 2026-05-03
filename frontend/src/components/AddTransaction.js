import React, { useState } from 'react';
import { api } from '../services/api';
import Toast from './Toast';

function AddTransaction({ portfolioId, onTransactionAdded }) {
  const [formData, setFormData] = useState({
    symbol: '',
    transaction_type: 'buy',
    quantity: '',
    price: ''
  });
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.symbol.trim()) {
      setToast({ message: 'Please enter a stock symbol', type: 'error' });
      return;
    }
    
    if (parseFloat(formData.quantity) <= 0) {
      setToast({ message: 'Quantity must be greater than 0', type: 'error' });
      return;
    }
    
    if (parseFloat(formData.price) <= 0) {
      setToast({ message: 'Price must be greater than 0', type: 'error' });
      return;
    }

    setLoading(true);
    
    try {
      await api.addTransaction({
        portfolio_id: portfolioId,
        ...formData,
        quantity: parseFloat(formData.quantity),
        price: parseFloat(formData.price)
      });
      
      setToast({ message: '✅ Transaction added successfully!', type: 'success' });
      setFormData({ symbol: '', transaction_type: 'buy', quantity: '', price: '' });
      onTransactionAdded();
    } catch (error) {
      setToast({ 
        message: error.response?.data?.detail || 'Failed to add transaction', 
        type: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="add-transaction">
        <h3>Add Transaction</h3>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Stock Symbol (e.g., AAPL)"
            value={formData.symbol}
            onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
            required
            disabled={loading}
          />
          <select
            value={formData.transaction_type}
            onChange={(e) => setFormData({...formData, transaction_type: e.target.value})}
            disabled={loading}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          <input
            type="number"
            step="0.01"
            placeholder="Quantity"
            value={formData.quantity}
            onChange={(e) => setFormData({...formData, quantity: e.target.value})}
            required
            disabled={loading}
            min="0.01"
          />
          <input
            type="number"
            step="0.01"
            placeholder="Price"
            value={formData.price}
            onChange={(e) => setFormData({...formData, price: e.target.value})}
            required
            disabled={loading}
            min="0.01"
          />
          <button type="submit" disabled={loading}>
            {loading ? '⏳ Adding...' : 'Add Transaction'}
          </button>
        </form>
      </div>
    </>
  );
}

export default AddTransaction;