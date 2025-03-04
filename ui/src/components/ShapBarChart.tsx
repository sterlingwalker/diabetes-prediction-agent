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
  annotationPlugin,
);

const ShapBarChart = ({ shapResponse }) => {
  const { shapValues, shapBaseValue, modelUsed } = shapResponse;

  const features = Object.keys(shapValues);
  const values = Object.values(shapValues);

  const data = {
    labels: features,
    datasets: [
      {
        label: "SHAP Value",
        data: values,
        backgroundColor: values.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 0.6)" : "rgba(255, 99, 132, 0.6)",
        ),
        borderColor: values.map((val) =>
          val >= 0 ? "rgba(75, 192, 192, 1)" : "rgba(255, 99, 132, 1)",
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
      annotation: {
        annotations: {
          shapBaseLine: {
            type: "line" as const,
            yMin: shapBaseValue,
            yMax: shapBaseValue,
            borderColor: "red",
            borderWidth: 2,
            borderDash: [6, 6],
            label: {
              enabled: true,
              content: `Base Value: ${shapBaseValue.toFixed(3)}`,
              position: "start" as const,
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
          text: "SHAP Value",
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

export default ShapBarChart;
