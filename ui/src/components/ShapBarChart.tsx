import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

// 1. Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ShapBarChart = ({ shapResponse }) => {
  const { shapValues, shapBaseValue } =
    shapResponse;

  // 2. Prepare chart data & options
  const features = Object.keys(shapValues);
  const values = Object.values(shapValues);

  const data = {
    labels: features,
    datasets: [
      {
        label: "SHAP Value",
        data: values,
        backgroundColor: values.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 0.6)" : "rgba(255, 99, 132, 0.6)"
        ),
        borderColor: values.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 1)" : "rgba(255, 99, 132, 1)"
        ),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "SHAP Values by Feature",
      },
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `SHAP Contribution: ${context.parsed.y.toFixed(4)}`;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Features",
        },
      },
      y: {
        title: {
          display: true,
          text: "SHAP Value",
        },
      },
    },
  };

  // 3. Render the bar chart
  return (
    <div style={{ width: "100%", margin: "0 auto" }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default ShapBarChart;