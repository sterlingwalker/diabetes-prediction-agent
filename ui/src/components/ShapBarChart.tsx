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
  const shapImpacts = Object.values(shapValues);

  // Sort features by absolute SHAP impact (biggest first)
  const sortedIndices = shapImpacts
    .map((_, i) => i)
    .sort((a, b) => Math.abs(shapImpacts[b]) - Math.abs(shapImpacts[a]));
  const sortedFeatures = sortedIndices.map((i) => features[i]);
  const sortedShapValues = sortedIndices.map((i) => shapImpacts[i]);

  // Compute cumulative SHAP values for proper stacking
  let cumulative = shapBaseValue;
  const startPositions = [];
  const endPositions = [];

  sortedShapValues.forEach((val) => {
    startPositions.push(cumulative);
    cumulative += val;
    endPositions.push(cumulative);
  });

  // Prepare chart data
  const data = {
    labels: sortedFeatures,
    datasets: [
      {
        label: "SHAP Contribution",
        data: sortedShapValues,
        backgroundColor: sortedShapValues.map((val) =>
          val >= 0 ? "rgba(54, 162, 235, 0.7)" : "rgba(255, 99, 132, 0.7)" // 🔵 Blue for Positive, 🔴 Red for Negative
        ),
        borderColor: sortedShapValues.map((val) =>
          val >= 0 ? "rgba(54, 162, 235, 1)" : "rgba(255, 99, 132, 1)"
        ),
        borderWidth: 1,
        base: startPositions, // ✅ Correct base stacking logic
      },
    ],
  };

  // Chart options with proper stacking
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
          baseLine: {
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
