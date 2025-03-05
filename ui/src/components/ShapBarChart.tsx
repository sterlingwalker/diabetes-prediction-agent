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

  // ✅ Compute explicit cumulative SHAP values for proper stacking
  let cumulative = shapBaseValue;
  const startPositions = [shapBaseValue]; // First bar starts at `shapBaseValue`

  sortedShapValues.forEach((val) => {
    cumulative += val;
    startPositions.push(cumulative); // Store where each bar should start
  });

  // ✅ Create explicit start positions for stacking
  const stackedData = sortedShapValues.map((val, idx) => ({
    feature: sortedFeatures[idx],
    shapValue: val,
    startPos: startPositions[idx], // Ensures each bar starts at correct cumulative position
  }));

  // ✅ Prepare chart data (Separate dataset for background stacking)
  const data = {
    labels: stackedData.map((d) => d.feature),
    datasets: [
      {
        label: "Support Bars",
        data: stackedData.map((d) => d.startPos - shapBaseValue), // Pushes bars to correct stacking
        backgroundColor: "rgba(0, 0, 0, 0)", // Fully transparent
        borderWidth: 0,
      },
      {
        label: "SHAP Contribution",
        data: stackedData.map((d) => d.shapValue),
        backgroundColor: stackedData.map((d) =>
          d.shapValue >= 0 ? "rgba(255, 99, 132, 0.7)" : "rgba(75, 192, 75, 0.7)" // 🔴 Red for Positive, 🟢 Green for Negative
        ),
        borderColor: stackedData.map((d) =>
          d.shapValue >= 0 ? "rgba(255, 99, 132, 1)" : "rgba(75, 192, 75, 1)"
        ),
        borderWidth: 1,
      },
    ],
  };

  // ✅ Chart options with true waterfall stacking
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
