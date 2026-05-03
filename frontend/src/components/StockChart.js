import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from 'chart.js';
import { api } from '../services/api';

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

function StockChart({ symbol }) {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    if (!symbol) return;

    const fetchChart = async () => {
      try {
        const res = await api.getStockHistory(symbol); // backend API
        const data = res.data;

        setChartData({
          labels: data.map(item => item.date),
          datasets: [
            {
              label: symbol,
              data: data.map(item => item.price),
              borderColor: '#2563eb',
              backgroundColor: 'rgba(37,99,235,0.1)',
              tension: 0.4
            }
          ]
        });
      } catch (err) {
        console.error("Chart error:", err);
      }
    };

    fetchChart();
  }, [symbol]);

  if (!chartData) return <p>Loading chart...</p>;

  return (
    <div className="card">
      <h3>{symbol} Price Chart</h3>
      <Line data={chartData} />
    </div>
  );
}

export default StockChart;