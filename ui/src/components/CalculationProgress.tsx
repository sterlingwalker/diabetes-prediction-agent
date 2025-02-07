import * as React from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material/styles";
import ConstructionIcon from "@mui/icons-material/Construction";

const CalculationProgressContainer = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  width: "100%",
  height: 200,
  padding: theme.spacing(3),
  borderRadius: `calc(${theme.shape.borderRadius}px + 4px)`,
  border: "1px solid ",
  borderColor: (theme.vars || theme).palette.divider,
  background:
    "linear-gradient(to bottom right, hsla(220, 35%, 97%, 0.3) 25%, hsla(220, 20%, 88%, 0.3) 100%)",
  boxShadow: "0px 4px 8px hsla(210, 0%, 0%, 0.05)",
  [theme.breakpoints.up("xs")]: {
    height: 200,
  },
  [theme.breakpoints.up("sm")]: {
    height: 200,
  },
  ...theme.applyStyles("dark", {
    background:
      "linear-gradient(to right bottom, hsla(220, 30%, 6%, 0.2) 25%, hsla(220, 20%, 25%, 0.2) 100%)",
    boxShadow: "0px 4px 8px hsl(220, 35%, 0%)",
  }),
}));

export default function CalculationProgress() {
  return (
    <Stack spacing={{ xs: 3, sm: 6 }} useFlexGap>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <CalculationProgressContainer>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="subtitle2">
              IN PROGRESS: Integration with CopilotKit
            </Typography>
            <ConstructionIcon sx={{ color: "text.secondary" }} />
          </Box>
        </CalculationProgressContainer>
      </Box>
    </Stack>
  );
}
