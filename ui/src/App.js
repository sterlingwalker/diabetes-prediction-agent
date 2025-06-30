import React, { useState } from "react";
import "./App.css";
import Predictor from "./components/Predictor.tsx";
import McpClient from "./components/McpClient.tsx";
import Button from "@mui/material/Button";

function App() {
  const [showMcp, setShowMcp] = useState(false);
  return (
    <div className="App">
      <Button onClick={() => setShowMcp(!showMcp)} sx={{ mt: 2 }}>
        {showMcp ? "Back to Predictor" : "Open MCP Client"}
      </Button>
      {showMcp ? <McpClient /> : <Predictor />}
    </div>
  );
}

export default App;
