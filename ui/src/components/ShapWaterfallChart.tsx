import React from "react";

const ShapWaterfallChart = ({ shapResponse }) => {
  const { shapPlot } = shapResponse;

  return (
    <div style={{ width: "100%", margin: "0 auto" }}>
      <p>SHAP Chart Explaining your probability calculation</p>
      <img
        width={"100%"}
        src={`data:image/png;base64,${shapPlot}`}
        alt="SHAP Visualization"
      />
    </div>
  );
};

export default ShapWaterfallChart;
