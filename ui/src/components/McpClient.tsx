import React, { useState } from "react";
import axios from "axios";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";

const actions = [
  { value: "list_models", label: "List Models" },
  { value: "switch_model", label: "Switch Model" },
  { value: "current_model", label: "Current Model" },
  { value: "metadata", label: "Metadata" },
  { value: "predict", label: "Predict" },
  { value: "recommendations", label: "Recommendations" },
  { value: "chat", label: "Chat" },
];

const defaultParams: Record<string, any> = {
  list_models: {},
  switch_model: { model: "lightgbm" },
  current_model: {},
  metadata: {},
  predict: {
    PatientName: "Alice",
    Glucose: 90,
    BloodPressure: 80,
    BMI: 25.0,
    Age: 30,
    Gender: 1,
    Ethnicity: 3,
  },
  recommendations: {
    PatientName: "Alice",
    Glucose: 90,
    BloodPressure: 80,
    BMI: 25.0,
    Age: 30,
    Gender: 1,
    Ethnicity: 3,
  },
  chat: {
    history: [{ role: "user", content: "Hi" }],
    user_input: "What does my risk mean?",
    patient_data: {
      PatientName: "Alice",
      Glucose: 90,
      BloodPressure: 80,
      BMI: 25.0,
      Age: 30,
      Gender: 1,
      Ethnicity: 3,
    },
    recommendations: { finalRecommendation: "See your doctor" },
    predicted_risk: "No Diabetes",
    risk_probability: "0.2",
  },
};

export default function McpClient() {
  const [action, setAction] = useState("list_models");
  const [parameters, setParameters] = useState(
    JSON.stringify(defaultParams["list_models"], null, 2),
  );
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    try {
      const params = parameters.trim() ? JSON.parse(parameters) : undefined;
      const res = await axios.post("/mcp", { action, parameters: params });
      setResponse(JSON.stringify(res.data, null, 2));
    } catch (err: any) {
      setResponse(`Error: ${err.message}`);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: 600,
        mx: "auto",
        mt: 4,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Typography variant="h5">MCP Client</Typography>
      <TextField
        select
        label="Action"
        value={action}
        onChange={(e) => {
          const val = e.target.value;
          setAction(val);
          setParameters(JSON.stringify(defaultParams[val] ?? {}, null, 2));
        }}
      >
        {actions.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label="Parameters (JSON)"
        value={parameters}
        onChange={(e) => setParameters(e.target.value)}
        multiline
        minRows={4}
      />
      <Button variant="contained" onClick={handleSubmit}>
        Send
      </Button>
      {response && (
        <TextField
          label="Response"
          value={response}
          multiline
          minRows={8}
          InputProps={{ readOnly: true }}
        />
      )}
    </Box>
  );
}
