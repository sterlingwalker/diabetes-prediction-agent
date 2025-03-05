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

  // Sort by absolute SHAP impact for better readability
  const sortedIndices = rawValues.map((_, i) => i).sort((a, b) => Math.abs(rawValues[b]) - Math.abs(rawValues[a]));
  const sortedFeatures = sortedIndices.map((i) => features[i]);
  const sortedValues = sortedIndices.map((i) => rawValues[i]);

  // Compute cumulative SHAP values for waterfall effect
  let cumulative = shapBaseValue;
  const cumulativeValues = sortedValues.map((val) => {
    const prev = cumulative;
    cumulative += val;
    return prev;
  });

  const data = {
    labels: sortedFeatures, // Only feature names without values
    datasets: [
      {
        label: "SHAP Value",
        data: sortedValues,
        backgroundColor: sortedValues.map((val) =>
          val >= 0 ? "rgba(255, 99, 132, 0.7)" : "rgba(54, 162, 235, 0.7)" // Red for positive, Blue for negative
        ),
        borderColor: sortedValues.map((val) =>
          val >= 0 ? "rgba(255, 99, 132, 1)" : "rgba(54, 162, 235, 1)"
        ),
        borderWidth: 1,
        base: cumulativeValues,
      },
    ],
  };

  const options = {
    indexAxis: "y", // Horizontal bars
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
            xMin: shapBaseValue,
            xMax: shapBaseValue,
            borderColor: "black",
            borderWidth: 2,
            borderDash: [6, 6],
            label: {
              enabled: true,
              content: `Base Value: ${shapBaseValue.toFixed(3)}`,
              position: "end",
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
          text: "SHAP Contribution",
        },
      },
      y: {
        title: {
          display: false, // Hide y-axis title since feature names are self-explanatory
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
