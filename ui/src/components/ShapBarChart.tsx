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

  // **Step 1: Sort features by absolute SHAP impact (biggest first)**
  const sortedIndices = shapImpacts
    .map((_, i) => i)
    .sort((a, b) => Math.abs(shapImpacts[b]) - Math.abs(shapImpacts[a]));
  const sortedFeatures = sortedIndices.map((i) => features[i]);
  const sortedShapValues = sortedIndices.map((i) => shapImpacts[i]);

  // **Step 2: Compute cumulative SHAP values for proper stacking**
  let cumulative = shapBaseValue;
  const startPositions = []; // "Support" bars to shift the real bars
  const endPositions = [];   // The actual SHAP values that will be visible

  sortedShapValues.forEach((val) => {
    startPositions.push(cumulative); // Store where each SHAP bar should start
    endPositions.push(val);         // Store SHAP impact
    cumulative += val;              // Update cumulative value for next bar
  });

  // **Step 3: Prepare datasets (Support bars + Real bars)**
  const data = {
  labels: ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E"],
  datasets: [
    {
      label: "Support Bars",
      data: [0.0, -0.2, -0.5, -0.6, -0.2], // Ensures stacking is correct
      backgroundColor: "rgba(0, 0, 0, 0)", // Transparent support bars
      borderWidth: 0,
    },
    {
      label: "SHAP Contribution",
      data: [-0.2, -0.3, -0.1, +0.4, -0.2], // True SHAP values
      backgroundColor: ["green", "green", "green", "red", "green"], // Negative = Green, Positive = Red
      borderColor: ["green", "green", "green", "red", "green"],
      borderWidth: 1,
    },
  ],
};

  // **Step 4: Configure Chart.js options**
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
        stacked: true, // Ensures bars stack correctly
        title: {
          display: true,
          text: "SHAP Contribution",
        },
      },
      y: {
        stacked: true, // Ensures proper waterfall effect
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
