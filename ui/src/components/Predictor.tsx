import React, { useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CssBaseline from "@mui/material/CssBaseline";
import Grid from "@mui/material/Grid2";
import Stack from "@mui/material/Stack";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import Typography from "@mui/material/Typography";
import ChevronLeftRoundedIcon from "@mui/icons-material/ChevronLeftRounded";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import PatientForm from "./PatientForm.tsx";
import Info from "./Info.tsx";
import InfoMobile from "./InfoMobile.tsx";
import CalculationProgress from "./CalculationProgress.tsx";
import Review from "./Review.tsx";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import AppTheme from "../theme/AppTheme.tsx";
import axios from "axios";
import ColorModeIconDropdown from "../theme/ColorModeIconDropdown.tsx";

const steps = ["Patient Details", "Calculate Diagnosis", "Review Results"];

export default function Predictor(props: { disableCustomTheme?: boolean }) {
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false); // Track API calls

  const [formData, setFormData] = useState({
    Pregnancies: "",
    Glucose: "",
    BloodPressure: "",
    SkinThickness: "",
    Insulin: "",
    BMI: "",
    DiabetesPedigreeFunction: "",
    Age: "",
  });

  const handleNext = async () => {
    if (activeStep === 0) {
      await handleSubmit();
    }
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      console.log("Sending prediction request with:", formData);
      const response = await axios.post("http://localhost:8000/predict", formData);
      
      console.log("Prediction response received:", response.data);
      setResult(response.data);
      setError(null);

      // Fetch recommendations **after** receiving a valid prediction
      await getRecommendations(response.data);
    } catch (err) {
      console.error("Prediction error:", err);
      setError("An error occurred while fetching the prediction.");
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async (predictionResult: any) => {
    setLoading(true);
    try {
      console.log("Sending recommendation request with:", formData);
      const response = await axios.post("http://localhost:8000/recommendations", formData);
      
      console.log("Recommendation response received:", response.data);
      setRecommendation(response.data);
      setError(null);
    } catch (err) {
      console.error("Recommendation error:", err);
      setError("An error occurred while fetching the recommendations.");
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <PatientForm formData={formData} setFormData={setFormData} />;
      case 1:
        return (
          <CalculationProgress
            predictionLoading={loading && !result}
            prediction={result}
            recommendationLoading={loading && !recommendation}
            error={error}
          />
        );
      case 2:
        return recommendation ? (
          <Review response={recommendation} />
        ) : (
          <p>Loading recommendations...</p>
        );
      default:
        throw new Error("Unknown step");
    }
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box sx={{ position: "fixed", top: "1rem", right: "1rem" }}>
        <ColorModeIconDropdown />
      </Box>

      <Grid container sx={{ minHeight: "100vh", mt: { xs: 4, sm: 0 } }}>
        <Grid
          size={{ xs: 12, sm: 5, lg: 4 }}
          sx={{
            display: { xs: "none", md: "flex" },
            flexDirection: "column",
            backgroundColor: "background.paper",
            borderRight: { md: "1px solid" },
            borderColor: { md: "divider" },
            alignItems: "start",
            pt: 16,
            px: 10,
            gap: 4,
          }}
        >
          <Typography variant="h4">
            <HealthAndSafetyIcon /> Diabetes Predictor
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", flexGrow: 1, width: "100%", maxWidth: 500 }}>
            <Info />
          </Box>
        </Grid>
        <Grid
          size={{ sm: 12, md: 7, lg: 8 }}
          sx={{
            display: "flex",
            flexDirection: "column",
            width: "100%",
            backgroundColor: { sm: "background.default" },
            alignItems: "start",
            pt: { sm: 16 },
            px: { xs: 2, sm: 10 },
            gap: { xs: 4, md: 8 },
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "space-between", width: "100%", maxWidth: 600 }}>
            <Stepper id="desktop-stepper" activeStep={activeStep} sx={{ width: "100%", height: 40 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>

          {getStepContent(activeStep)}

          <Box sx={{ display: "flex", flexGrow: 1, width: "100%", maxWidth: 600, justifyContent: "space-between" }}>
            {activeStep !== 0 && (
              <Button startIcon={<ChevronLeftRoundedIcon />} onClick={handleBack} variant="text">
                Previous
              </Button>
            )}
            <Button variant="contained" endIcon={<ChevronRightRoundedIcon />} onClick={handleNext}>
              {activeStep === steps.length - 1 ? "Continue Conversation" : "Next"}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </AppTheme>
  );
}
