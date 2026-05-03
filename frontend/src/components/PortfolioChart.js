import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function PortfolioChart({ stats }) {
  if (!stats || !stats.holdings) return null;

  // Generate mock historical data (last 30 days)
  const generateHistoricalData = () => {
    const days = 30;
    const data = [];
    const labels = [];
    const currentValue = stats.current_value;
    const startValue = stats.total_investment;

    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
      
      // Simulate growth from investment to current value
      const progress = (days - i) / days;
      const value = startValue + (currentValue - startValue) * progress;
      const randomVariation = value * (Math.random() * 0.02 - 0.01); // ±1% variation
      data.push((value + randomVariation).toFixed(2));
    }

    return { labels, data };
  };

  const { labels, data } = generateHistoricalData();

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Portfolio Value',
        data,
        borderColor: stats.total_profit_loss >= 0 ? '#16a34a' : '#dc2626',
        backgroundColor: stats.total_profit_loss >= 0 
          ? 'rgba(22, 163, 74, 0.1)' 
          : 'rgba(220, 38, 38, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => `$${Number(context.parsed.y).toLocaleString()}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`
        }
      }
    }
  };

  return (
    <div className="portfolio-chart-container">
      <h3>📈 Portfolio Growth (Last 30 Days)</h3>
      <div style={{ height: '300px' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}

export default PortfolioChart;