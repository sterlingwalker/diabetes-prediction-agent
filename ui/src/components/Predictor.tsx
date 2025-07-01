import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CssBaseline from "@mui/material/CssBaseline";
import Grid from "@mui/material/Grid2";
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
import ChatComponent from "./ChatComponent.tsx";
import Disclaimer from "./Disclaimer.tsx";

const steps = [
  "Patient Details",
  "Calculate Diagnosis",
  "Review Results",
  "Chat with Specialist",
];

export default function Predictor(props: { disableCustomTheme?: boolean }) {
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [showNextButton, setShowNextButton] = useState(false);
  const [modalOpen, setModalOpen] = useState(true);

  const [formData, setFormData] = useState({
    Glucose: "",
    BloodPressure: "",
    BMI: "",
    Age: "",
    Gender: "",
    Ethnicity: "",
  });

  useEffect(() => {
    if (activeStep === 1) {
      setShowNextButton(recommendation !== null);
    } else {
      setShowNextButton(
        activeStep !== 3 &&
          (activeStep > 0 ||
            Object.values(formData).every((value) => value !== "")),
      );
    }
  }, [activeStep, formData, recommendation]);

  const handleNext = () => {
    if (activeStep === 0) {
      handleSubmit();
    }
    setActiveStep(activeStep + 1);
  };

  const handleBack = () => {
    if (activeStep === 1) {
      setResult(null);
      setRecommendation(null);
      setError(null);
    }
    setActiveStep(activeStep - 1);
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post(
        "https://diabetes-675059836631.us-central1.run.app/predict",
        formData,
      );
      if (response.data.error) {
        setError(response.data.error);
        return;
      }
      setResult(response.data);
      setError(null);
      getRecommendations();
    } catch (err) {
      console.error(err);
      setError("An error occurred while fetching the prediction.");
    }
  };

  const getRecommendations = async () => {
    try {
      const response = await axios.post(
        "https://diabetes-675059836631.us-central1.run.app/recommendations",
        formData,
      );
      setRecommendation(response.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("An error occurred while fetching the recommendations.");
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <PatientForm formData={formData} setFormData={setFormData} />;
      case 1:
        return (
          <CalculationProgress
            predictionLoading={!result && !error}
            prediction={result}
            recommendationLoading={!recommendation && !error}
            error={error}
          />
        );
      case 2:
        return <Review response={recommendation} />;
      case 3:
        return (
          <ChatComponent
            patientData={formData}
            recommendations={recommendation}
            predictedRisk={result?.predictedRisk || ""}
            riskProbability={result?.riskProbability || ""}
          />
        );
      default:
        throw new Error("Unknown step");
    }
  };

  return (
    <React.Fragment>
      <AppTheme {...props}>
        <CssBaseline enableColorScheme />
        <Box sx={{ position: "fixed", top: "1rem", right: "1rem" }}>
          <ColorModeIconDropdown />
        </Box>
        <Grid
          container
          sx={{
            height: { xs: "100%", sm: "100%" },
            minHeight: { sm: "100vh" },
            mt: { xs: 4, sm: 0 },
          }}
        >
          <Grid
            size={{ xs: 12, sm: 5, lg: 4 }}
            sx={{
              display: { xs: "none", md: "flex" },
              flexDirection: "column",
              backgroundColor: "background.paper",
              borderRight: { sm: "none", md: "1px solid" },
              borderColor: { sm: "none", md: "divider" },
              alignItems: "start",
              pt: 16,
              px: 10,
              gap: 4,
            }}
          >
            <Typography variant="h4">
              <HealthAndSafetyIcon /> Diabetes Predictor
            </Typography>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                flexGrow: 1,
                width: "100%",
                maxWidth: 500,
              }}
            >
              <Info />
              <Button
                sx={{ width: "100%", mt: "auto", mb: "16px" }}
                onClick={() => setModalOpen(true)}
              >
                Disclaimer
              </Button>
            </Box>
          </Grid>
          <Grid
            size={{ sm: 12, md: 7, lg: 8 }}
            sx={{
              display: "flex",
              flexDirection: "column",
              maxWidth: "100%",
              width: "100%",
              backgroundColor: { xs: "transparent", sm: "background.default" },
              alignItems: "start",
              pt: { xs: 0, sm: 16 },
              px: { xs: 2, sm: 10 },
              gap: { xs: 4, md: 8 },
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: { sm: "space-between", md: "flex-end" },
                alignItems: "center",
                width: "100%",
                maxWidth: { sm: "100%", md: 600 },
                margin: "0 auto",
              }}
            >
              <Box
                sx={{
                  display: { xs: "none", md: "flex" },
                  flexDirection: "column",
                  justifyContent: "space-between",
                  alignItems: "flex-end",
                  flexGrow: 1,
                }}
              >
                <Stepper
                  id="desktop-stepper"
                  activeStep={activeStep}
                  sx={{ width: "100%", height: 40 }}
                >
                  {steps.map((label) => (
                    <Step
                      key={label}
                      sx={{
                        ":first-child": { pl: 0 },
                        ":last-child": { pr: 0 },
                      }}
                    >
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            </Box>
            <Card sx={{ display: { xs: "flex", md: "none" }, width: "100%" }}>
              <CardContent
                sx={{
                  display: "flex",
                  width: "100%",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <InfoMobile />
              </CardContent>
            </Card>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                flexGrow: 1,
                width: "100%",
                maxWidth: { sm: "100%" },
                gap: { xs: 5, md: "none" },
              }}
            >
              <React.Fragment>
                {getStepContent(activeStep)}
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: { xs: "column-reverse", sm: "row" },
                    alignItems: "end",
                    flexGrow: 1,
                    gap: 1,
                    pb: { xs: 12, sm: 0 },
                    mt: { xs: 2, sm: 0 },
                    mb: "60px",
                    justifyContent:
                      activeStep !== 0 ? "space-between" : "flex-end",
                  }}
                >
                  {activeStep !== 0 && (
                    <Button
                      startIcon={<ChevronLeftRoundedIcon />}
                      onClick={handleBack}
                      variant="text"
                    >
                      Previous
                    </Button>
                  )}
                  {showNextButton && (
                    <Button
                      variant="contained"
                      endIcon={<ChevronRightRoundedIcon />}
                      onClick={handleNext}
                    >
                      {activeStep === 2 ? "Chat with a Specialist" : "Next"}
                    </Button>
                  )}
                </Box>
              </React.Fragment>
            </Box>
          </Grid>
        </Grid>
      </AppTheme>
      <Disclaimer modalOpen={modalOpen} setModalOpen={setModalOpen} />
    </React.Fragment>
  );
}
