import * as React from "react";
import Grid from "@mui/material/Grid2";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import ReactMarkdown from "react-markdown";
import "../App.css";

export default function Review({ response }) {
  return (
    <div className="reviewContainer">
      <Typography
        sx={{ fontWeight: 400, fontSize: "20px", marginBottom: "16px" }}
        variant="subtitle2"
        gutterBottom
      >
        Recommendations
      </Typography>
      <Grid container>
        <React.Fragment>
          <Stack direction="column" spacing={1} sx={{ width: "100%", mb: 5 }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 400,
                fontSize: "16px",
                color: "text.secondary",
              }}
            >
              Endocrinologist:
            </Typography>
            <Typography
              variant="body2"
              sx={{ textAlign: "left", whiteSpace: "pre-wrap" }}
            >
              <ReactMarkdown>{response?.endocrinologistRecommendation}</ReactMarkdown>
            </Typography>
          </Stack>
        </React.Fragment>
        <React.Fragment>
          <Stack direction="column" spacing={1} sx={{ width: "100%", mb: 5 }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 400,
                fontSize: "16px",
                color: "text.secondary",
              }}
            >
              Dietician:
            </Typography>
            <Typography
              variant="body2"
              sx={{ textAlign: "left", whiteSpace: "pre-wrap" }}
            >
              <ReactMarkdown>{response?.dietitianRecommendation}</ReactMarkdown>
            </Typography>
          </Stack>
        </React.Fragment>
        <React.Fragment>
          <Stack direction="column" spacing={1} sx={{ width: "100%", mb: 5 }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 400,
                fontSize: "16px",
                color: "text.secondary",
              }}
            >
              Fitness Trainer:
            </Typography>
            <Typography
              variant="body2"
              sx={{ textAlign: "left", whiteSpace: "pre-wrap" }}
            >
              <ReactMarkdown>{response?.fitnessRecommendation}</ReactMarkdown>
            </Typography>
          </Stack>
        </React.Fragment>
        <React.Fragment>
          <Stack direction="column" spacing={1} sx={{ width: "100%", mb: 5 }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 400,
                fontSize: "16px",
                color: "text.secondary",
              }}
            >
              Overall Recommendation:
            </Typography>
            <Typography
              variant="body2"
              sx={{ textAlign: "left", whiteSpace: "pre-wrap" }}
            >
              <ReactMarkdown>{response?.finalRecommendation}</ReactMarkdown>
            </Typography>
          </Stack>
        </React.Fragment>
      </Grid>
    </div>
  );
}
