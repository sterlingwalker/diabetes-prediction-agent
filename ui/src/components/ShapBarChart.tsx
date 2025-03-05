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
import annotationPlugin from "chartjs-plugin-annotation";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin
);

const ShapWaterfallChart = ({ shapResponse }) => {
  const { shapValues, shapBaseValue, modelUsed } = shapResponse;

  const features = Object.keys(shapValues);
  const rawValues = Object.values(shapValues);

  // Compute cumulative SHAP values for waterfall effect
  let cumulative = shapBaseValue;
  const cumulativeValues = rawValues.map((val) => {
    const prev = cumulative;
    cumulative += val;
    return prev; // Start position for each bar
  });

  const data = {
    labels: features,
    datasets: [
      {
        label: "SHAP Value",
        data: rawValues, // Actual SHAP impact per feature
        backgroundColor: rawValues.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 0.6)" : "rgba(255, 99, 132, 0.6)"
        ),
        borderColor: rawValues.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 1)" : "rgba(255, 99, 132, 1)"
        ),
        borderWidth: 1,
        base: cumulativeValues, // Waterfall effect starts from cumulative base
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "SHAP Waterfall Chart",
      },
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `SHAP Contribution: ${context.raw.toFixed(4)}`;
          },
        },
      },
      annotation: {
        annotations: {
          shapBaseLine: {
            type: "line",
            yMin: shapBaseValue,
            yMax: shapBaseValue,
            borderColor: "red",
            borderWidth: 2,
            borderDash: [6, 6],
            label: {
              enabled: true,
              content: `Base Value: ${shapBaseValue.toFixed(3)}`,
              position: "start",
              xAdjust: 10,
              backgroundColor: "rgba(0,0,0,0.7)",
              color: "#fff",
            },
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
          text: "SHAP Value (Cumulative)",
        },
      },
    },
  };

  return (
    <div style={{ width: "100%", margin: "0 auto" }}>
      <h3>Model Used: {modelUsed}</h3>
      <p>SHAP Base Value: {shapBaseValue.toFixed(4)}</p>
      <Bar data={data} options={options} />
    </div>
  );
};

export default ShapWaterfallChart;
