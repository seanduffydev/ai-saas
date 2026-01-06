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

// Register Chart.js components
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

function ForecastChart({ historicalData, predictions, commodityInfo }) {
  if (!historicalData || !predictions) {
    return <div>No data to display</div>;
  }

  // Prepare chart data
  const historicalDates = historicalData.map(d => d.date);
  const historicalPrices = historicalData.map(d => d.price);
  
  const predictionDates = predictions.map(d => d.date);
  const predictionPrices = predictions.map(d => d.price);

  const data = {
    labels: [...historicalDates, ...predictionDates],
    datasets: [
      {
        label: 'Historical Prices',
        data: [...historicalPrices, ...Array(predictions.length).fill(null)],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      },
      {
        label: 'LSTM Predictions',
        data: [...Array(historicalData.length).fill(null), ...predictionPrices],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 3,
        pointBackgroundColor: 'rgb(255, 99, 132)',
        tension: 0.1
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${commodityInfo?.name || 'Commodity'} Price Forecast`,
        font: {
          size: 18
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += commodityInfo?.unit ? 
                `${context.parsed.y.toFixed(2)} ${commodityInfo.unit}` : 
                `$${context.parsed.y.toFixed(2)}`;
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date'
        },
        ticks: {
          maxTicksLimit: 10
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: commodityInfo?.unit || 'Price (USD)'
        }
      }
    }
  };

  return (
    <div className="chart-container">
      <Line data={data} options={options} />
    </div>
  );
}

export default ForecastChart;