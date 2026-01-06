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

function ComparisonChart({ historicalData, lstmPredictions, transformerPredictions, commodityInfo }) {
  if (!historicalData || !lstmPredictions || !transformerPredictions) {
    return <div>No data to display</div>;
  }

  const historicalDates = historicalData.map(d => d.date);
  const historicalPrices = historicalData.map(d => d.price);
  
  const lstmDates = lstmPredictions.map(d => d.date);
  const lstmPrices = lstmPredictions.map(d => d.price);
  
  const transformerDates = transformerPredictions.map(d => d.date);
  const transformerPrices = transformerPredictions.map(d => d.price);

  const data = {
    labels: [...historicalDates, ...lstmDates],
    datasets: [
      {
        label: 'Historical Prices',
        data: [...historicalPrices, ...Array(lstmPredictions.length).fill(null)],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1
      },
      {
        label: 'LSTM Predictions',
        data: [...Array(historicalData.length).fill(null), ...lstmPrices],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 3,
        pointBackgroundColor: 'rgb(255, 99, 132)',
        tension: 0.1
      },
      {
        label: 'Transformer Predictions',
        data: [...Array(historicalData.length).fill(null), ...transformerPrices],
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        borderWidth: 2,
        borderDash: [10, 5],
        pointRadius: 3,
        pointBackgroundColor: 'rgb(54, 162, 235)',
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
        text: `${commodityInfo?.name || 'Commodity'} - LSTM vs Transformer Comparison`,
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

export default ComparisonChart;