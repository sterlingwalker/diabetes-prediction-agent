import React from "react";

const ShapWaterfallChart = ({ shapResponse }) => {
  const { shapBaseValue, shapPlot } = shapResponse;


  return (
    <div style={{ width: "100%", margin: "0 auto" }}>
      <p>Base Percentage: {shapBaseValue.toFixed(4) * 100}</p>
      <img width={'100%'} src={`data:image/png;base64,${shapPlot}`} alt="SHAP Visualization" />
    </div>
  );
};

export default ShapWaterfallChart;
