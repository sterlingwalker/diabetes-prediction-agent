import React from "react";
import "./App.css";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import Predictor from "./components/Predictor.tsx";

function App() {
  return (
    <div className="App">
      <Predictor />
    </div>
  );
}

export default App;
