import * as React from "react";
import Grid from "@mui/material/Grid2";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

const responses = [
  {
    name: "Endocrinologist:",
    detail: `Based on the patient data provided, I would recommend the following treatment plan for this patient:
1. Lifestyle modifications: The patient should be advised to make necessary....`,
  },
  {
    name: "Dietician:",
    detail: `Dietary Plan:
1. Meal Frequency: Encourage the patient to eat 3 main meals and 2-3 small snacks throughout the day to maintain blood sugar levels.
2. Carbohydrate Intake: The patient should `,
  },
  {
    name: "Fitness:",
    detail: `Exercise Plan for a Patient with "No Diabetes" Risk:
1. Warm-up: A 5-minute warm-up is essential before starting any exercise routine. It can include light cardio exercises such as walking or jogging in place, followed by some dynamic stretches to loosen up the muscles.
2. Cardiovascular Exercise: Aim for at least 30 minutes.. `,
  },
  {
    name: "Summary:",
    detail: `Final Consolidated Plan for Sarah Smith:
1. Lifestyle modifications: Follow a balanced, nutritious diet...`,
  },
];

export default function Review() {
  return (
    <Stack spacing={2}>
      <div>
        <Typography variant="subtitle2" gutterBottom>
          Recommendations
        </Typography>
        <Grid container>
          {responses.map((response) => (
            <React.Fragment key={response.name}>
              <Stack
                direction="column"
                spacing={1}
                sx={{ width: "100%", mb: 1 }}
              >
                <Typography variant="body1" sx={{ color: "text.secondary" }}>
                  {response.name}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ textAlign: "left", whiteSpace: "pre-wrap" }}
                >
                  {response.detail}
                </Typography>
              </Stack>
            </React.Fragment>
          ))}
        </Grid>
      </div>
    </Stack>
  );
}
