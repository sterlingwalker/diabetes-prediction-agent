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

export default function McpClient() {
  const [action, setAction] = useState("list_models");
  const [parameters, setParameters] = useState("{}");
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
        onChange={(e) => setAction(e.target.value)}
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
