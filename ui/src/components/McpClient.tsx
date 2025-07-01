import React, { useState } from "react";
import axios, { AxiosError } from "axios";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";

// Parameter Types
interface PatientData {
  PatientName: string;
  Glucose: number;
  BloodPressure: number;
  BMI: number;
  Age: number;
  Gender: number;
  Ethnicity: number;
}

interface PredictParams extends PatientData {}
interface RecommendationsParams extends PatientData {}

interface SwitchModelParams {
  model: string;
}

interface ChatHistoryItem {
  role: "user" | "assistant" | "system";
  content: string;
}

interface ChatParams {
  history: ChatHistoryItem[];
  user_input: string;
  patient_data: PatientData;
  recommendations: { finalRecommendation: string };
  predicted_risk: string;
  risk_probability: string;
}

// Type for all possible action parameters
interface ActionParams {
  list_models: Record<string, never>; // Explicitly no params
  switch_model: SwitchModelParams;
  current_model: Record<string, never>;
  metadata: Record<string, never>;
  predict: PredictParams;
  recommendations: RecommendationsParams;
  chat: ChatParams;
}

// Type for action keys
type ActionKey = keyof ActionParams;

const actions: { value: ActionKey; label: string }[] = [
  { value: "list_models", label: "List Models" },
  { value: "switch_model", label: "Switch Model" },
  { value: "current_model", label: "Current Model" },
  { value: "metadata", label: "Metadata" },
  { value: "predict", label: "Predict" },
  { value: "recommendations", label: "Recommendations" },
  { value: "chat", label: "Chat" },
];

const defaultParams: ActionParams = {
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
  const [action, setAction] = useState<ActionKey>("list_models");
  const [parameters, setParameters] = useState<string>(
    JSON.stringify(defaultParams[action], null, 2),
  );
  const [response, setResponse] = useState<string>("");
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleActionChange = (newAction: ActionKey) => {
    setAction(newAction);
    setParameters(JSON.stringify(defaultParams[newAction] ?? {}, null, 2));
    setJsonError(null); // Clear JSON error when action changes
  };

  const handleParametersChange = (newParamsStr: string) => {
    setParameters(newParamsStr);
    try {
      JSON.parse(newParamsStr);
      setJsonError(null);
    } catch (e) {
      if (e instanceof Error) {
        setJsonError("Invalid JSON: " + e.message);
      } else {
        setJsonError("Invalid JSON format.");
      }
    }
  };

  const handleSubmit = async () => {
    if (jsonError) {
      setResponse("Error: Invalid JSON in parameters.");
      return;
    }
    setIsLoading(true);
    setResponse(""); // Clear previous response

    try {
      const parsedParams = parameters.trim() ? JSON.parse(parameters) : undefined;

      console.log("MCP Request:", {
        action: action,
        parameters: parsedParams
      });

      const res = await axios.post("/mcp", { action, parameters: parsedParams });
      setResponse(JSON.stringify(res.data, null, 2));
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const axiosError = err as AxiosError;
        let errorMsg = `Error: ${axiosError.message}`;
        if (axiosError.response && axiosError.response.data) {
          errorMsg += ` - ${JSON.stringify(axiosError.response.data)}`;
        }
        setResponse(errorMsg);
      } else if (err instanceof Error) {
        setResponse(`Error: ${err.message}`);
      } else {
        setResponse("An unknown error occurred");
      }
    } finally {
      setIsLoading(false);
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
        error={!!jsonError}
        helperText={jsonError}
      />
      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={isLoading || !!jsonError}
      >
        {isLoading ? <CircularProgress size={24} /> : "Send"}
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
