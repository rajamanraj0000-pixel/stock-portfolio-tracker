import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { exportToCSV } from '../utils/exportCSV';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';

function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      // Get user's portfolios
      const portfoliosResponse = await api.getPortfolios();
      
      if (portfoliosResponse.data.length > 0) {
        const portfolioId = portfoliosResponse.data[0].id;
        const response = await api.getTransactions(portfolioId);
        setTransactions(response.data);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setToast({ message: 'Failed to load transactions', type: 'error' });
      setLoading(false);
    }
  };

  const handleExport = () => {
    const exportData = transactions.map(txn => ({
      Date: new Date(txn.transaction_date).toLocaleDateString(),
      Symbol: txn.symbol,
      Type: txn.transaction_type.toUpperCase(),
      Quantity: txn.quantity,
      Price: txn.price,
      Total: (txn.quantity * txn.price).toFixed(2)
    }));
    
    exportToCSV(exportData, 'transactions');
    setToast({ message: 'Transactions exported successfully!', type: 'success' });
  };

  return (
    <>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      
      <div className="page-container">
        <div className="page-header">
          <div>
            <h1>💸 Transactions</h1>
            <p>View all your buy and sell history</p>
          </div>
          {transactions.length > 0 && (
            <button onClick={handleExport} className="export-button">
              📥 Export CSV
            </button>
          )}
        </div>

        {loading ? (
          <LoadingSpinner message="Loading transactions..." />
        ) : transactions.length === 0 ? (
          <div className="empty-state">
            <p>📭 No transactions yet</p>
            <p>Add your first transaction from the Portfolio page!</p>
          </div>
        ) : (
          <div className="transactions-section">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Total Value</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr key={txn.id}>
                    <td>{new Date(txn.transaction_date).toLocaleString()}</td>
                    <td><strong>{txn.symbol}</strong></td>
                    <td>
                      <span className={`txn-badge ${txn.transaction_type}`}>
                        {txn.transaction_type.toUpperCase()}
                      </span>
                    </td>
                    <td>{txn.quantity}</td>
                    <td>${txn.price.toFixed(2)}</td>
                    <td>${(txn.quantity * txn.price).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}

export default TransactionsPage;