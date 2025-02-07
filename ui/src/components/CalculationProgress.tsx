import * as React from "react";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material/styles";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CircularProgress from "@mui/material/CircularProgress";

const CalculationProgressContainer = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(2),
  width: "70%",
  height: "100%",
  padding: theme.spacing(3),
  borderRadius: `calc(${theme.shape.borderRadius}px + 4px)`,
  border: "1px solid ",
  borderColor: (theme.vars || theme).palette.divider,
  background:
    "linear-gradient(to bottom right, hsla(220, 35%, 97%, 0.3) 25%, hsla(220, 20%, 88%, 0.3) 100%)",
  boxShadow: "0px 4px 8px hsla(210, 0%, 0%, 0.05)",
  ...theme.applyStyles("dark", {
    background:
      "linear-gradient(to right bottom, hsla(220, 30%, 6%, 0.2) 25%, hsla(220, 20%, 25%, 0.2) 100%)",
    boxShadow: "0px 4px 8px hsl(220, 35%, 0%)",
  }),
}));

export default function CalculationProgress({
  predictionLoading,
  prediction,
  recommendationLoading,
  error,
}) {
  const isDiabetic = prediction?.predictedRisk === "Diabetes";
  const riskProbability = prediction?.riskProbability;

  const determineRiskColor = () => {
    if (riskProbability < 30) {
      return "success";
    } else if (riskProbability < 70) {
      return "warning";
    } else {
      return "error";
    }
  };

  if (error) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
        }}
      >
        <Typography variant="h6" color="error">
          Error: {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
    >
      <CalculationProgressContainer>
        {predictionLoading ? (
          <Box sx={{ display: "flex", gap: "16px" }}>
            <Box sx={{ display: "flex", margin: "0 0 0 8px" }}>
              <CircularProgress size={20} />
            </Box>
            <Typography variant="subtitle2">Loading Prediction...</Typography>
          </Box>
        ) : (
          <Box sx={{ display: "flex", gap: "16px", margin: "0 0 0 8px" }}>
            <Box sx={{ display: "flex" }}>
              <CheckCircleIcon />
            </Box>
            <Typography variant="subtitle2">Prediction Complete</Typography>
          </Box>
        )}
        <Box sx={{ display: "flex", width: "100%" }}>
          {isDiabetic ? (
            <Alert variant="outlined" severity="warning" sx={{ width: "100%" }}>
              You are likely to be diabetic
            </Alert>
          ) : (
            <Alert
              variant="outlined"
              severity="success"
              color="success"
              sx={{ width: "100%" }}
            >
              Your probability of having diabetes is low
            </Alert>
          )}
        </Box>
        <Box sx={{ display: "flex" }}>
          <Alert
            variant="outlined"
            severity={determineRiskColor()}
            sx={{ width: "100%" }}
          >
            {`Probability of developing Diabetes: ${riskProbability}%`}
          </Alert>
        </Box>
        {recommendationLoading ? (
          <Box sx={{ display: "flex", gap: "16px", margin: "0 0 16px 8px" }}>
            <Box sx={{ display: "flex" }}>
              <CircularProgress size={20} />
            </Box>
            <Typography variant="subtitle2">
              Loading Recommendations...
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: "flex", gap: "16px", margin: "0 0 16px 8px" }}>
            <Box sx={{ display: "flex" }}>
              <CheckCircleIcon />
            </Box>
            <Typography variant="subtitle2">Recommendation Complete</Typography>
          </Box>
        )}
      </CalculationProgressContainer>
    </Box>
  );
}
